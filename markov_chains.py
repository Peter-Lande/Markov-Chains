import json
import random
import argparse
import sys


class MarkovSystem:
    def __init__(self, state_length: int = 1, save_filename: str = 'markov_system.json') -> None:
        self.state_dictionary: dict[str, dict[str, int]] = {}
        self.state_length: int = state_length
        self.save_file = save_filename

    def __populate_system(self, word_list: list[str]) -> None:
        k_length_states = [' '.join(word_list[i:i+self.state_length])
                           for i, _ in enumerate(word_list[:-self.state_length])]
        if len(self.state_dictionary) == 0:
            self.state_dictionary = {k_state: {} for k_state in set(k_length_states)}
        else:
            new_markov_dictionary = {k_state: {} for k_state in set(k_length_states)}
            self.state_dictionary = new_markov_dictionary | self.state_dictionary
        for index, k_length_state in enumerate(k_length_states[:-1]):
            if k_length_states[index+1] in self.state_dictionary[k_length_state]:
                self.state_dictionary[k_length_state][k_length_states[index+1].split()[-1]] += 1
            else:
                self.state_dictionary[k_length_state][k_length_states[index+1].split()[-1]] = 1

    def load_text(self, filename: str) -> None:
        self.__populate_system(clean_input_text(filename))

    def save(self) -> None:
        with open(self.save_file, 'w') as f:
            json.dump(self.state_dictionary, f)

    def load(self) -> None:
        with open(self.save_file, 'r') as f:
            self.state_dictionary = json.load(f)

    def sample_next_state(self, current_state: str):
        next_state_vector_weights = [weight for weight in self.state_dictionary[current_state].values()]
        next_state_vector = [key for key in self.state_dictionary[current_state].keys()]
        return random.choices(next_state_vector, next_state_vector_weights)[0]

    def stochastic_chain(self, seed: str = None, chain_length: int = 15) -> str:
        if seed:
            try:
                if self.state_dictionary[seed]:
                    sentence = seed
                    for i in range(chain_length):
                        sentence += ' '
                        sentence += self.sample_next_state(' '.join(sentence.split()[i: i+self.state_length]))
                    return sentence
            except KeyError:
                return 'Seed does not exist in Markov chain. Aborting.'
        else:
            seed = random.choices(list(self.state_dictionary.keys()))[0]
            sentence = seed
            for i in range(chain_length):
                sentence += ' '
                sentence += self.sample_next_state(' '.join(sentence.split()[i: i+self.state_length]))
        return sentence


def clean_input_text(filename: str) -> list[str]:
    text = ""
    with open(filename, 'r') as f:
        text += f.read()
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace('“', ' " ')
    text = text.replace('”', ' " ')
    text = text.replace('_', '')
    for spaced in ['.', '-', ',', '!', '?', '(', '—', ')', ';']:
        text = text.replace(spaced, ' {0} '.format(spaced))
    text_list = text.split(' ')
    text_list = [word for word in text_list if word != '']
    return text_list


def clean_output_text(output_text: str) -> str:
    if output_text[0] in ['.', '-', ',', '!', '?', '(', '—', ')', '"', ';']:
        output_text = output_text[1:]
    if output_text[0].islower():
        output_text = output_text[0].upper() + output_text[1:]
    if not output_text[-1] in ['.', '!', '?']:
        output_text = output_text + random.choices(['.', '!', '?'])[0]
    for spaced in [' . ', ' - ', ' , ', ' ! ', ' ? ', ' ( ', ' — ', ' ) ', ' ; ', ' " ']:
        if spaced in [' - ', ' — ']:
            output_text = output_text.replace(spaced, '{0}'.format(spaced.strip()))
        else:
            output_text = output_text.replace(spaced, '{0} '.format(spaced.strip()))
    return output_text


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='A command for generating Markov Chains of texts and producing sentences based on the texts.', usage='%(prog)s [options]')
parser.add_argument('-g', '--gen', help='Generate a Markov system from a given text file. Can use -k and -o to change the number of words per state and the output file resepectively.',
                    nargs='?', metavar='input_filename', const='input.txt')
parser.add_argument('-k', help='Changes the length of the Markov state to the given number of words.',
                    nargs='?', metavar='state_length', default=2, const=2)
parser.add_argument('-o', '--output', help='Changes where the file in which the Markov system is stored.',
                    nargs='?', metavar='output_file', const='markov_system.json', default='markov_system.json')
parser.add_argument('-a', '--append', nargs='?', help='Add data to an existing Markov system.',
                    metavar='input_filename', const='input.txt')
parser.add_argument('-l', '--length', metavar='chain_length',
                    help='Changes the length of the outputted chain from the Markov system.', default=15)
parser.add_argument('-i', '--input', nargs='?', metavar='input_filename',
                    help='Input file to use for generating Markov chains.', const='markov_system.json')
parser.add_argument('-s', '--seed', nargs='?', help='Initial state of Markov system.', metavar='seed')


if __name__ == "__main__":
    args = parser.parse_args()
    args_dict = {key: value for key, value in vars(args).items() if value}
    markov_system = MarkovSystem(int(args_dict['k']))
    if 'gen' in args_dict.keys():
        try:
            markov_system.save_file = args_dict['output']
            markov_system.load_text(args_dict['gen'])
            markov_system.save()
        except FileNotFoundError:
            print('File does not exist. Aborting.')
            sys.exit()
        except ValueError:
            print('Invalid state length. Aborting.')
            sys.exit()
    elif 'input' in args_dict.keys():
        markov_system.save_file = args_dict['input']
        markov_system.load()
        if 'seed' in args_dict.keys():
            print(clean_output_text(markov_system.stochastic_chain(args_dict['seed'], args_dict['length'])))
        else:
            print(clean_output_text(markov_system.stochastic_chain(chain_length=args_dict['length'])))
    elif 'append' in args_dict.keys():
        markov_system.save_file = args_dict['output']
        markov_system.load()
        markov_system.load_text(args_dict['append'])
        markov_system.save()
