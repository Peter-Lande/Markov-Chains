import json
import random
import argparse
import sys


def clean_input_text(filename: str) -> list[str]:
    text = ""
    with open(filename, 'r') as f:
        text += f.read()
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace('“', ' " ')
    text = text.replace('”', ' " ')
    for spaced in ['.', '-', ',', '!', '?', '(', '—', ')', ';']:
        text = text.replace(spaced, ' {0} '.format(spaced))
    text_list = text.split(' ')
    text_list = [word for word in text_list if word != '']
    return text_list


def create_word_dictionary(word_list: list[str], state_length: int = 2, word_dict: dict[str, dict[str, int]] = None) -> dict[str, dict[str, int]]:
    k_length_states = [' '.join(word_list[i:i+state_length]) for i, _ in enumerate(word_list[:-state_length])]
    if not word_dict:
        word_dict = {k_state: {} for k_state in set(k_length_states)}
    else:
        new_word_dict = {k_state: {} for k_state in set(k_length_states)}
        word_dict = new_word_dict | word_dict
    for i, x in enumerate(k_length_states[:-1]):
        if k_length_states[i+1] in word_dict[x]:
            word_dict[x][k_length_states[i+1].split()[-1]] += 1
        else:
            word_dict[x][k_length_states[i+1].split()[-1]] = 1
    return word_dict


def save_dictionary(word_dictionary: dict[str, dict[str, int]], filename: str = 'markov_system.json') -> None:
    with open(filename, 'w') as f:
        json.dump(word_dictionary, f)


def load_dictionary(filename: str = 'markov_system.json') -> dict[str, dict[str, int]]:
    with open(filename, 'r') as f:
        return json.load(f)


def sample_next_state(word_dict: dict[str, dict[str, int]], current_state: str):
    next_state_vector_weights = [weight for weight in word_dict[current_state].values()]
    next_state_vector = [key for key in word_dict[current_state].keys()]
    return random.choices(next_state_vector, next_state_vector_weights)[0]


def stochastic_chain(word_dictionary: dict[str, dict[str, int]], seed: str = None, chain_length: int = 15) -> str:
    k = len(list(word_dictionary.keys())[0].split())
    if seed:
        try:
            if word_dictionary[seed]:
                sentence = seed
                for i in range(chain_length):
                    sentence += ' '
                    sentence += sample_next_state(word_dictionary, ' '.join(sentence.split()[i: i+k]))
                return sentence
        except KeyError:
            return 'Seed does not exist in Markov chain. Aborting.'
    else:
        seed = random.choices(list(word_dictionary.keys()))[0]
        sentence = seed
        for i in range(chain_length):
            sentence += ' '
            sentence += sample_next_state(word_dictionary, ' '.join(sentence.split()[i: i+k]))
        return sentence


def clean_output_text(output_text: str) -> str:
    if output_text[0] in ['.', '-', ',', '!', '?', '(', '—', ')', '"']:
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
                    nargs='?', metavar='output_file', const='markov_system.json')
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
    if 'gen' in args_dict.keys():
        try:
            word_dict = create_word_dictionary(clean_input_text(args_dict['gen']), int(args_dict['k']))
        except FileNotFoundError:
            print('File does not exist. Aborting.')
            sys.exit()
        except ValueError:
            print('Invalid state length. Aborting.')
            sys.exit()
        if 'output' in args_dict.keys():
            save_dictionary(word_dict, args_dict['output'])
        else:
            save_dictionary(word_dict)
    elif 'input' in args_dict.keys():
        word_dict = load_dictionary(args_dict['input'])
        if 'seed' in args_dict.keys():
            print(clean_output_text(stochastic_chain(word_dict, args_dict['seed'], args_dict['length'])))
        else:
            print(clean_output_text(stochastic_chain(word_dict, chain_length=args_dict['length'])))
    elif 'append' in args_dict.keys():
        if 'output' in args_dict.keys():
            word_dict = load_dictionary(args_dict['output'])
        else:
            word_dict = load_dictionary()
        word_dict = create_word_dictionary(clean_input_text(
            args_dict['append']), len(list(word_dict.keys())[0].split()), word_dict)
        if 'output' in args_dict.keys():
            save_dictionary(word_dict, args_dict['output'])
        else:
            save_dictionary(word_dict)
