
import re
import time
from itertools import combinations

from helpers.loghelpers import LOG
from helpers.ipfshelpers import add_json, get_json
from validators.validators import valid_address, valid_bech32_address
from taghash.taghash import TagHash
from inputs.inputs import get_sil
from linker.linker import get_lal


class HivemindIssue(object):
    def __init__(self, question_hash=None):
        """
        Constructor of Hivemind class

        :param question_hash: The ipfs hash of the hivemind question
        """
        self.hivemind_id = None
        self.questions = []
        self.description = ''
        self.tags = None
        self.answer_type = 'String'
        self.consensus_type = 'Single'  # Single or Ranked: Is the expected result of this question a single answer or a ranked list?
        self.constraints = None

        if question_hash is not None:
            self.load(hivemind_hash=question_hash)

    def add_question(self, question):
        if isinstance(question, (str, unicode)) and question not in self.questions:
            self.questions.append(question)

    def set_description(self, description):
        if isinstance(description, (str, unicode)):
            self.description = description

    def set_tags(self, tags):
        if isinstance(tags, (str, unicode)):
            self.tags = tags

    def set_answer_type(self, answer_type):
        if answer_type in ['String', 'Bool', 'Integer', 'Float', 'Hivemind', 'Image', 'Video', 'Complex', 'Address']:
            self.answer_type = answer_type
        else:
            raise Exception('Invalid answer_type: %s (must be one of the following: "String", "Bool", "Integer", "Float", "Hivemind", "Image", "Video", "Complex", "Address")' % answer_type)

    def set_consensus_type(self, consensus_type):
        if consensus_type in ['Single', 'Ranked']:
            self.consensus_type = consensus_type
        else:
            raise Exception('Consensus_type must be either Single or Ranked, got %s' % consensus_type)

    def set_constraints(self, constraints):
        if not isinstance(constraints, dict):
            raise Exception('constraints must be a dict, got %s' % type(constraints))

        if 'specs' in constraints:
            specs = constraints['specs']
            if not isinstance(constraints['specs'], dict):
                raise Exception('constraint "specs" must be a dict, got %s' % type(specs))

            for key in specs:
                if specs[key] not in ['String', 'Integer', 'Float']:
                    raise Exception('Spec type must be String or Integer or Float, got %s' % specs[key])

        for constraint_type in ['min_length', 'max_length', 'min_value', 'max_value', 'decimals']:
            if constraint_type in constraints and not isinstance(constraints[constraint_type], (int, float, long)):
                raise Exception('Value of constraint %s must be a number' % constraint_type)

        for constraint_type in ['regex']:
            if constraint_type in constraints and not isinstance(constraints[constraint_type], (str, unicode)):
                raise Exception('Value of constraint %s must be a string' % constraint_type)

        for constraint_type in ['choices']:
            if constraint_type in constraints and not isinstance(constraints[constraint_type], list):
                raise Exception('Value of constraint %s must be a list' % constraint_type)

        for constraint_type in ['SIL', 'LAL']:
            if constraint_type in constraints and not (valid_address(constraints[constraint_type]) or valid_bech32_address(constraints[constraint_type])):
                raise Exception('Value of constraint %s must be a valid address' % constraint_type)

        if 'LAL' in constraints and 'xpub' not in constraints:
            raise Exception('Constraints that include a LAL must also have a xpub specified!')

        for constraint_type in ['block_height']:
            if constraint_type in constraints and not isinstance(constraints[constraint_type], (int, long)):
                raise Exception('Value of constraint %s must be a integer' % constraint_type)

        if all([key in ['min_length', 'max_length', 'min_value', 'max_value', 'decimals', 'regex', 'specs', 'choices', 'SIL', 'LAL', 'xpub', 'block_height'] for key in constraints.keys()]):
            self.constraints = constraints
        else:
            raise Exception('constraints contain an invalid key: %s' % constraints)

    def id(self):
        taghash = TagHash(tags=self.questions[0])
        taghash.add_tag(tag=self.answer_type)
        if self.tags is not None:
            taghash.add_tag(tag=self.tags)

        self.hivemind_id = taghash.get()
        return self.hivemind_id

    def info(self):
        """
        Get info about the hivemind question

        :return: A string containing info about the hivemind question
        """
        info = 'Hivemind ID: %s\n' % self.hivemind_id
        info += 'Hivemind question: %s\n' % self.questions[0]
        info += 'Hivemind description: %s\n' % self.description
        info += 'Hivemind tags: %s\n' % self.tags
        info += 'Answer type: %s\n' % self.answer_type

        for constraint_type, constraint_value in self.constraints.items():
            info += 'Constraint %s: %s\n' % (constraint_type, constraint_value)

        for i, additional_question in enumerate(self.questions[1:]):
            info += 'Additional question %s: %s\n' % (i + 1, additional_question)

        return info

    def save(self):
        hivemind_data = {'hivemind_id': self.id(),
                         'questions': self.questions,
                         'description': self.description,
                         'tags': self.tags,
                         'answer_type': self.answer_type,
                         'consensus_type': self.consensus_type,
                         'constraints': self.constraints}

        return add_json(hivemind_data)

    def load(self, hivemind_hash):
        hivemind_data = get_json(hivemind_hash)

        self.questions = hivemind_data['questions']
        self.description = hivemind_data['description']
        self.tags = hivemind_data['tags']
        self.answer_type = hivemind_data['answer_type']
        self.consensus_type = hivemind_data['consensus_type']
        self.constraints = hivemind_data['constraints']
        self.hivemind_id = self.id()


class HivemindOption(object):
    def __init__(self, option_hash=None):
        """
        Constructor of the Option object

        :param option_hash: The multihash of the Option (optional)
        """
        self.option_hash = option_hash

        self.hivemind_issue_hash = None
        self.hivemind_issue = None

        self.value = None
        self.answer_type = None  # can be 'String', 'Bool', 'Integer', 'Float', 'Hivemind', 'Image', 'Video', 'Complex', 'Address'

        if self.option_hash is not None:
            self.load(option_hash=option_hash)

    def set_hivemind_issue(self, hivemind_issue_hash):
        self.hivemind_issue_hash = hivemind_issue_hash
        self.hivemind_issue = HivemindIssue(question_hash=self.hivemind_issue_hash)
        self.answer_type = self.hivemind_issue.answer_type

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

        if not self.is_valid():
            raise Exception('Invalid value for answer type %s: %s' % (self.answer_type, value))

    def is_valid(self):
        if not isinstance(self.hivemind_issue, HivemindIssue):
            raise Exception('No hivemind question set on option yet! Must set the hivemind question first before setting the value!')

        if self.answer_type != self.hivemind_issue.answer_type:
            LOG.error('Option value is not the correct answer type, got %s but should be %s' % (self.answer_type, self.hivemind_issue.answer_type))
            return False

        if self.hivemind_issue.constraints is not None and 'choices' in self.hivemind_issue.constraints:
            if self.value not in self.hivemind_issue.constraints['choices']:
                LOG.error('Option %s is not valid because this it is not in the allowed choices of this hiveminds constraints!' % self.value)
                raise Exception('Option %s is not valid because this it is not in the allowed choices of this hiveminds constraints!' % self.value)

        if self.answer_type == 'String' and self.is_valid_string_option():
            return True
        elif self.answer_type == 'Bool' and self.is_valid_bool_option():
            return True
        elif self.answer_type == 'Integer' and self.is_valid_integer_option():
            return True
        elif self.answer_type == 'Float' and self.is_valid_float_option():
            return True
        elif self.answer_type == 'Hivemind' and self.is_valid_hivemind_option():
            return True
        elif self.answer_type == 'Image' and isinstance(self.value, (str, unicode)):  # todo check for valid ipfs hash
            return True
        elif self.answer_type == 'Video' and isinstance(self.value, (str, unicode)):  # todo check for valid ipfs hash
            return True
        elif self.answer_type == 'Complex' and self.is_valid_complex_option():
            return True
        elif self.answer_type == 'Address' and self.is_valid_address_option():
            return True
        else:
            return False

    def is_valid_string_option(self):
        if not isinstance(self.value, (str, unicode)):
            return False

        if self.hivemind_issue.constraints is not None:
            if 'min_length' in self.hivemind_issue.constraints and len(self.value) < self.hivemind_issue.constraints['min_length']:
                return False
            elif 'max_length' in self.hivemind_issue.constraints and len(self.value) > self.hivemind_issue.constraints['max_length']:
                return False
            elif 'regex' in self.hivemind_issue.constraints and re.match(pattern=self.hivemind_issue.constraints['regex'], string=self.value) is None:
                return False

        return True

    def is_valid_float_option(self):
        if not isinstance(self.value, float):
            LOG.error('Option value %s is not a floating number value but instead is a %s' % (self.value, type(self.value)))
            return False

        if self.hivemind_issue.constraints is not None:
            if 'min_value' in self.hivemind_issue.constraints and self.value < self.hivemind_issue.constraints['min_value']:
                LOG.error('Option value is below minimum value: %s < %s' % (self.value, self.hivemind_issue.constraints['min_value']))
                return False
            elif 'max_value' in self.hivemind_issue.constraints and self.value > self.hivemind_issue.constraints['max_value']:
                LOG.error('Option value is above maximum value: %s > %s' % (self.value, self.hivemind_issue.constraints['max_value']))
                return False
            elif 'decimals' in self.hivemind_issue.constraints and 0 < self.hivemind_issue.constraints['decimals'] != len(str(self.value)) - 1 - str(self.value).find('.'):
                LOG.error('Option value does not have the correct number of decimals (%s): %s' % (self.hivemind_issue.constraints['decimals'], self.value))
                return False

        return True

    def is_valid_integer_option(self):
        if not isinstance(self.value, (int, long)):
            LOG.error('Option value %s is not a integer value but instead is a %s' % (self.value, type(self.value)))
            return False

        if self.hivemind_issue.constraints is not None:
            if 'min_value' in self.hivemind_issue.constraints and self.value < self.hivemind_issue.constraints['min_value']:
                LOG.error('Option value is below minimum value: %s < %s' % (self.value, self.hivemind_issue.constraints['min_value']))
                return False
            elif 'max_value' in self.hivemind_issue.constraints and self.value > self.hivemind_issue.constraints['max_value']:
                LOG.error('Option value is above maximum value: %s > %s' % (self.value, self.hivemind_issue.constraints['max_value']))
                return False

        return True

    def is_valid_bool_option(self):
        if not isinstance(self.value, bool):
            LOG.error('Option value %s is not a boolean value but instead is a %s' % (self.value, type(self.value)))
            return False

        return True

    def is_valid_hivemind_option(self):
        try:
            isinstance(HivemindIssue(question_hash=self.value), HivemindIssue)
        except Exception as ex:
            LOG.error('IPFS hash %s is not a valid hivemind: %s' % (self.value, ex))
            return False

        return True

    def is_valid_complex_option(self):
        if not isinstance(self.value, dict):
            return False

        if 'specs' in self.hivemind_issue.constraints:
            for spec_key in self.hivemind_issue.constraints['specs']:
                if spec_key not in self.value:
                    return False

            for spec_key in self.value.keys():
                if spec_key not in self.hivemind_issue.constraints['specs']:
                    return False

            for spec_key, spec_value in self.value.items():
                if self.hivemind_issue.constraints['specs'][spec_key] == 'String' and not isinstance(spec_value, (str, unicode)):
                    return False
                elif self.hivemind_issue.constraints['specs'][spec_key] == 'Integer' and not isinstance(spec_value, (int, long)):
                    return False
                elif self.hivemind_issue.constraints['specs'][spec_key] == 'Float' and not isinstance(spec_value, float):
                    return False

        return True

    def is_valid_address_option(self):
        if 'SIL' in self.hivemind_issue.constraints or 'LAL' in self.hivemind_issue.constraints:
            address = self.hivemind_issue.constraints['SIL']
            block_height = self.hivemind_issue.constraints['block_height'] if 'block_height' in self.hivemind_issue.constraints else 0

            if 'SIL' in self.hivemind_issue.constraints:
                data = get_sil(address=address, block_height=block_height)
                if 'SIL' not in data:
                    LOG.error('Unable to retrieve SIL of %s to verify constraints op hivemind option' % address)
                    return False

                for item in data['SIL']:
                    if item[0] == self.value:  # assume data in SIL is valid
                        return True

                return False

            elif 'LAL' in self.hivemind_issue.constraints:
                xpub = self.hivemind_issue.constraints['xpub']
                data = get_lal(address=address, xpub=xpub, block_height=block_height)
                if 'LAL' not in data:
                    LOG.error('Unable to retrieve LAL of %s to verify constraints of hivemind option' % address)
                    return False

                for item in data['LAL']:
                    if item[1] == self.value:  # assume data in LAL is valid
                        return True

                return False

        return valid_address(self.value) or valid_bech32_address(self.value)

    def info(self):
        """
        Get all details of the Option as a formatted string
        """
        ret = 'Option hash: %s' % self.option_hash
        ret += '\nAnswer type: %s' % self.answer_type
        ret += '\nOption value: %s' % self.value

        return ret

    def save(self):
        option_data = {'hivemind_question_hash': self.hivemind_issue_hash,
                       'answer_type': self.answer_type,
                       'value': self.value}

        self.option_hash = add_json(option_data)
        return self.option_hash

    def load(self, option_hash):
        option = get_json(option_hash)
        if not all(key in option for key in ['hivemind_question_hash', 'value', 'answer_type']):
            LOG.error('hivemind option json does not contain all necessary keys')
            raise Exception('Invalid hivemind option json data: %s' % option)

        self.hivemind_issue_hash = option['hivemind_question_hash']
        self.hivemind_issue = HivemindIssue(self.hivemind_issue_hash)

        self.value = option['value']
        self.answer_type = option['answer_type']


class HivemindOpinion(object):
    def __init__(self, opinion_hash=None):
        """
        Constructor of the Opinion object

        :param opinion_hash: The ipfs hash of the Opinion object (optional)
        """
        self.opinion_hash = opinion_hash
        self.opinionator = None

        self.hivemind_hash = None
        self.hivemind = None

        self.hivemind_state_hash = None
        self.hivemind_state = None

        self.ranked_choice = []
        self.auto_complete = None

        self.question_index = 0

        if opinion_hash is not None:
            self.load(opinion_hash=opinion_hash)

    def set(self, opinionator, ranked_choice):
        """
        Set the list of ranked option hashes

        :param opinionator: The id of the person expressing the opinion
        :param ranked_choice: A list of sorted option hashes
        """
        if not isinstance(self.hivemind_state, HivemindState):
            raise Exception('Hivemind state has not been set yet')

        self.opinionator = opinionator
        self.ranked_choice = ranked_choice

        if not self.is_valid():
            raise Exception('invalid ranked choice')

    def get(self):
        """
        Get the sorted list of option hashes

        :return: The list of sorted option ids
        """
        if self.hivemind_state.hivemind_issue.answer_type not in ['Integer', 'Float']:
            return self.ranked_choice
        elif self.auto_complete is None or len(self.ranked_choice) > 1:  # if more than one ranked choice is given, then auto_complete is overruled
            return self.ranked_choice
        elif self.auto_complete in ['MAX', 'MIN', 'CLOSEST', 'CLOSEST_HIGH', 'CLOSEST_LOW']:
            my_opinion_value = HivemindOption(option_hash=self.ranked_choice[0]).get()
            sorted_option_hashes = sorted(self.hivemind_state.options, key=lambda x: HivemindOption(option_hash=x).get())

            if self.auto_complete == 'MAX':
                completed_ranking = [option_hash for option_hash in sorted_option_hashes if HivemindOption(option_hash=option_hash).get() <= my_opinion_value]

            elif self.auto_complete == 'MIN':
                completed_ranking = [option_hash for option_hash in sorted_option_hashes if HivemindOption(option_hash=option_hash).get() >= my_opinion_value]

            elif self.auto_complete == 'CLOSEST':
                completed_ranking = sorted(self.hivemind_state.options, key=lambda x: abs(HivemindOption(option_hash=x).get() - my_opinion_value))

            elif self.auto_complete == 'CLOSEST_HIGH':
                completed_ranking = sorted(self.hivemind_state.options, key=lambda x: (abs(HivemindOption(option_hash=x).get() - my_opinion_value), -HivemindOption(option_hash=x).get()))

            elif self.auto_complete == 'CLOSEST_LOW':
                completed_ranking = sorted(self.hivemind_state.options, key=lambda x: (abs(HivemindOption(option_hash=x).get() - my_opinion_value), HivemindOption(option_hash=x).get()))

            else:
                raise Exception('Unknown auto_complete type: %s' % self.auto_complete)

            return completed_ranking

    def set_hivemind_state(self, hivemind_state_hash):
        self.hivemind_state_hash = hivemind_state_hash
        self.hivemind_state = HivemindState(state_hash=self.hivemind_state_hash)

    def set_question_index(self, question_index):
        self.question_index = question_index

    def get_unranked_option_ids(self):
        """
        Get the list of option ids that have not been ranked yet

        :return: A list of option ids that have not been ranked yet
        """
        unranked = []
        for option_id in self.hivemind.options:
            if option_id not in self.ranked_choice:
                unranked.append(option_id)

        return sorted(unranked)

    def info(self):
        """
        Get the details of this Opinion object in string format

        :return: the details of this Opinion object in string format
        """
        ret = '%s: ' % self.opinionator
        for i, option_hash in enumerate(self.ranked_choice):
            option = HivemindOption(option_hash=option_hash)
            ret += '\n%s: %s' % (i+1, option.get())

        return ret

    def is_complete(self, ranked_choice=None):
        """
        Is this Opinion complete? Meaning are all option hashes present in the ranked_choice?

        :param ranked_choice: An optional list of option hashes
        :return: True or False
        """
        if ranked_choice is None:
            ranked_choice = self.ranked_choice

        return all(option_id in ranked_choice for option_id in self.hivemind.options)

    def is_valid(self):
        """
        Is the Opinion object a valid opinion? Meaning are all option hashes in the ranked_choice valid?

        :return: True or False
        """
        if not isinstance(self.hivemind_state, HivemindState):
            return False

        if self.contains_duplicates() is True:
            return False

        return not any(option_hash not in self.hivemind_state.options for option_hash in self.ranked_choice)

    def contains_duplicates(self):
        """
        Does the Opinion object have duplicate option hashes in ranked_choice?

        :return: True or False
        """
        return len([x for x in self.ranked_choice if self.ranked_choice.count(x) >= 2]) > 0

    def save(self):
        opinion_data = {'hivemind_state_hash': self.hivemind_state_hash,
                        'opinionator': self.opinionator,
                        'ranked_choice': self.ranked_choice,
                        'auto_complete': self.auto_complete,
                        'question_index': self.question_index}

        self.opinion_hash = add_json(opinion_data)
        return self.opinion_hash

    def load(self, opinion_hash):
        opinion_data = get_json(opinion_hash)

        self.set_hivemind_state(hivemind_state_hash=opinion_data['hivemind_state_hash'])
        self.opinionator = opinion_data['opinionator']
        self.ranked_choice = opinion_data['ranked_choice']
        self.auto_complete = opinion_data['auto_complete']
        self.question_index = opinion_data['question_index']


class HivemindState(object):
    def __init__(self, state_hash=None):
        self.hivemind_issue_hash = None
        self.hivemind_issue = None
        self.options = []
        self.opinions = [{}]  # opinions are recorded for each question separately
        self.weights = {}
        self.results = [{}]  # results are recorded for each question separately
        self.contributions = [{}]  # contributions are recorded for each question separately
        self.previous_state_hash = None

        if state_hash is not None:
            self.load(state_hash)

    def set_hivemind_issue(self, issue_hash):
        self.hivemind_issue_hash = issue_hash
        self.hivemind_issue = HivemindIssue(question_hash=self.hivemind_issue_hash)
        self.opinions = [{} for _ in range(len(self.hivemind_issue.questions))]
        self.results = [{} for _ in range(len(self.hivemind_issue.questions))]
        self.contributions = [{} for _ in range(len(self.hivemind_issue.questions))]

    def load(self, hivemind_state_hash):
        hivemind_state_data = get_json(hivemind_state_hash)

        self.hivemind_issue_hash = hivemind_state_data['hivemind_issue_hash']
        self.options = hivemind_state_data['options']
        self.opinions = hivemind_state_data['opinions']
        self.weights = hivemind_state_data['weights']
        self.results = hivemind_state_data['results']
        self.contributions = hivemind_state_data['contributions']
        self.previous_state_hash = hivemind_state_data['previous_state']

        self.hivemind_issue = HivemindIssue(question_hash=self.hivemind_issue_hash)

    def save(self):
        hivemind_state_data = {'hivemind_issue_hash': self.hivemind_issue_hash,
                               'options': self.options,
                               'opinions': self.opinions,
                               'weights': self.weights,
                               'results': self.results,
                               'contributions': self.contributions,
                               'previous_state': self.previous_state_hash}

        state_hash = add_json(hivemind_state_data)
        self.previous_state_hash = state_hash
        return state_hash

    def clear_results(self, question_index=0):
        """
        Clear results of the hivemind
        """
        for opinionator in self.results[question_index]:
            self.results[question_index][opinionator] = {'win': 0, 'loss': 0, 'unknown': 0, 'score': 0}

    def add_option(self, option_hash):
        if not isinstance(self.hivemind_issue, HivemindIssue):
            return

        option = HivemindOption(option_hash)
        if isinstance(option, HivemindOption) and option.is_valid():
            if option_hash not in self.options:
                self.options.append(option_hash)
                for i in range(len(self.hivemind_issue.questions)):
                    self.results[i][option_hash] = {'win': 0, 'loss': 0, 'unknown': 0, 'score': 0}

    def add_opinion(self, opinion_hash, signature, weight=1.0, question_index=0):
        opinion = HivemindOpinion(opinion_hash=opinion_hash)
        if isinstance(opinion, HivemindOpinion) and opinion.is_valid():
            self.opinions[question_index][opinion.opinionator] = [opinion_hash, signature, int(time.time())]
            self.set_weight(opinionator=opinion.opinionator, weight=weight)

    def get_opinion(self, opinionator, question_index=0):
        """
        Get the Opinion object of a certain opinionator

        :param opinionator: The opinionator
        :param question_index: The index of the question in the HivemindQuestion (default=0)
        :return: An Opinion object
        """
        opinion = None
        if opinionator in self.opinions[question_index]:
            opinion = HivemindOpinion(opinion_hash=self.opinions[question_index][opinionator])

        return opinion

    def set_weight(self, opinionator, weight=1.0):
        """
        Set the weight of a Opinion

        :param opinionator: The opinionator
        :param weight: The weight of the Opinion (default=1.0)
        """
        self.weights[opinionator] = weight

    def get_weight(self, opinionator):
        """
        Get the weight of an Opinion

        :param opinionator: The opinionator
        :return: The weight of the Opinion (type float)
        """
        return self.weights[opinionator]

    def info(self):
        """
        Print the details of the hivemind
        """
        ret = "================================================================================="
        ret += '\nHivemind id: ' + self.hivemind_issue.hivemind_id
        ret += '\nHivemind main question: ' + self.hivemind_issue.questions[0]
        ret += '\nHivemind description: ' + self.hivemind_issue.description
        if self.hivemind_issue.tags is not None:
            ret += '\nHivemind tags: ' + self.hivemind_issue.tags
        ret += '\nAnswer type: ' + self.hivemind_issue.answer_type
        if self.hivemind_issue.constraints is not None:
            ret += '\nOption constraints: ' + str(self.hivemind_issue.constraints)
        ret += '\n' + "================================================================================="
        ret += '\n' + self.options_info()

        for i, question in enumerate(self.hivemind_issue.questions):
            ret += '\nHivemind question %s: %s' % (i, self.hivemind_issue.questions[i])
            ret += '\n' + self.opinions_info(question_index=i)
            ret += '\n' + self.results_info(question_index=i)

        return ret

    def options_info(self):
        """
        Get detailed information about the options as a formatted string

        :return: A string containing all information about the options
        """
        ret = "Options"
        ret += "\n======="
        for i, option_hash in enumerate(self.options):
            ret += '\nOption %s:' % (i + 1)
            option = HivemindOption(option_hash=option_hash)
            ret += '\n' + option.info()
            ret += '\n'

        return ret

    def opinions_info(self, question_index=0):
        """
        Print out a list of the Opinions of the hivemind
        """
        ret = "Opinions"
        ret += "\n========"
        # opinion_data is a list containing [opinion_hash, signature of 'IPFS=opinion_hash', timestamp]
        for opinionator, opinion_data in self.opinions[question_index].items():
            ret += '\nTimestamp: %s, Signature: %s' % (opinion_data[2], opinion_data[1])
            opinion = HivemindOpinion(opinion_hash=opinion_data[0])
            ret += '\n' + opinion.info()
            ret += '\n'

        return ret

    def calculate_results(self, question_index=0):
        """
        Calculate the results of the hivemind
        """
        LOG.info('Calculating results for question %s...' % question_index)
        self.clear_results(question_index=question_index)
        for a, b in combinations(self.options, 2):
            for opinionator in self.opinions[question_index]:
                winner = compare(a, b, self.opinions[question_index][opinionator][0])
                weight = self.weights[opinionator] if opinionator in self.weights else 0
                if winner == a:
                    self.results[question_index][a]['win'] += weight
                    self.results[question_index][b]['loss'] += weight
                elif winner == b:
                    self.results[question_index][b]['win'] += weight
                    self.results[question_index][a]['loss'] += weight
                elif winner is None:
                    self.results[question_index][a]['unknown'] += weight
                    self.results[question_index][b]['unknown'] += weight

        self.calculate_scores(question_index=question_index)
        self.calculate_contributions(question_index=question_index)
        results_info = self.results_info(question_index=question_index)
        for line in results_info.split('\n'):
            LOG.info(line)

    def calculate_scores(self, question_index=0):
        """
        Calculate the scores of all Options
        """
        for option_id in self.results[question_index]:
            if self.results[question_index][option_id]['win'] + self.results[question_index][option_id]['loss'] + self.results[question_index][option_id]['unknown'] > 0:
                self.results[question_index][option_id]['score'] = self.results[question_index][option_id]['win'] / float(
                    self.results[question_index][option_id]['win'] + self.results[question_index][option_id]['loss'] + self.results[question_index][option_id]['unknown'])

    def get_score(self, option_hash, question_index=0):
        return self.results[question_index][option_hash]['score']

    def get_options(self, question_index=0):
        """
        Get the list of Options as sorted by the hivemind

        :return: A list of Option objects sorted by highest score
        """
        return [HivemindOption(option_hash=option[0]) for option in sorted(self.results[question_index].items(), key=lambda x: x[1]['score'], reverse=True)]

    def consensus(self, question_index=0):
        sorted_options = self.get_options(question_index=question_index)
        if len(sorted_options) == 0:
            return None
        elif len(sorted_options) == 1:
            return sorted_options[0].value
        # Make sure the consensus is not tied between the first two options
        elif len(sorted_options) >= 2 and self.get_score(option_hash=sorted_options[0].option_hash) > self.get_score(option_hash=sorted_options[1].option_hash):
            return sorted_options[0].value
        else:
            return None

    def ranked_consensus(self, question_index=0):
        return [option.value for option in self.get_options(question_index=question_index)]

    def get_consensus(self, question_index=0):
        if self.hivemind_issue.consensus_type == 'Single':
            return self.consensus(question_index=question_index)
        elif self.hivemind_issue.consensus_type == 'Ranked':
            return self.ranked_consensus(question_index=question_index)

    def results_info(self, question_index=0):
        """
        Print out the results of the hivemind
        """
        ret = self.hivemind_issue.questions[question_index]
        ret += '\nResults:\n========'
        i = 0
        for option_hash, option_result in sorted(self.results[question_index].items(), key=lambda x: x[1]['score'], reverse=True):
            i += 1
            option = HivemindOption(option_hash=option_hash)
            ret += '\n%s: (%g%%) : %s' % (i, round(option_result['score']*100, 2), option.get())

        ret += '\n================'
        ret += '\nCurrent consensus: %s' % self.get_consensus(question_index=question_index)
        ret += '\n================'

        ret += '\nContributions:'
        ret += '\n================'
        for opinionator, contribution in self.contributions[question_index].items():
            ret += '\n%s: %s' % (opinionator, contribution)
        ret += '\n================'

        return ret

    def calculate_contributions(self, question_index):
        # Clear contributions
        self.contributions[question_index] = {}

        deviances = {}
        total_deviance = 0
        multipliers = {}

        # sort the option hashes by highest score
        option_hashes_by_score = [option[0] for option in sorted(self.results[question_index].items(), key=lambda x: x[1]['score'], reverse=True)]

        # sort the opinionators by the timestamp of their opinion
        opinionators_by_timestamp = [opinionator for opinionator, opinion_data in sorted(self.opinions[question_index].items(), key=lambda x: x[1][2])]

        for i, opinionator in enumerate(opinionators_by_timestamp):
            deviance = 0
            opinion = HivemindOpinion(opinion_hash=self.opinions[question_index][opinionator][0])

            # Calculate the 'early bird' multiplier (whoever gives their opinion first gets the highest multiplier, value is between 0 and 1), if opinion is an empty list, then multiplier is 0
            multipliers[opinionator] = 1 - (i/float(len(opinionators_by_timestamp))) if len(opinion.ranked_choice) > 0 else 0

            # Calculate the deviance of the opinion, the closer the opinion is to the final result, the lower the deviance
            for j, option_hash in enumerate(option_hashes_by_score):
                if option_hash in opinion.ranked_choice:
                    deviance += abs(j - opinion.ranked_choice.index(option_hash))
                else:
                    deviance += len(option_hashes_by_score)-j

            total_deviance += deviance
            deviances[opinionator] = deviance

        if total_deviance != 0:  # to avoid divide by zero
            self.contributions[question_index] = {opinionator: (1-(deviances[opinionator]/float(total_deviance)))*multipliers[opinionator] for opinionator in deviances}
        else:  # everyone has perfect opinion, but contributions should still be multiplied by the 'early bird' multiplier
            self.contributions[question_index] = {opinionator: 1*multipliers[opinionator] for opinionator in deviances}


def compare(a, b, opinion_hash):
    """
    Helper function to compare 2 Option objects against each other based on a given Opinion

    :param a: The first Option object
    :param b: The second Option object
    :param opinion_hash: The Opinion object
    :return: The Option that is considered better by the Opinion
    If one of the Options is not given in the Opinion object, the other option wins by default
    If both Options are not in the Opinion object, None is returned
    """
    opinion = HivemindOpinion(opinion_hash=opinion_hash)
    ranked_choice = opinion.ranked_choice
    if a in ranked_choice and b in ranked_choice:
        if ranked_choice.index(a) < ranked_choice.index(b):
            return a
        elif ranked_choice.index(a) > ranked_choice.index(b):
            return b
    elif a in ranked_choice:
        return a
    elif b in ranked_choice:
        return b
    else:
        return None
