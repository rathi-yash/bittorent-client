from bencoded_types import BencodedTypes


class Splitter:
    def __init__(self):
        self.TYPE_TO_SPLITTER_MAP = {
            BencodedTypes.INTEGER: self.split_off_bencoded_integer,
            BencodedTypes.STRING: self.split_off_bencoded_string,
            BencodedTypes.LIST: self.split_bencoded_list,
            BencodedTypes.DICT: self.split_bencoded_dictionary,
        }

    def split_off_bencoded_integer(self, bencoded_list):
        end_of_int = bencoded_list.find(b"e")
        return bencoded_list[: end_of_int + 1], bencoded_list[end_of_int + 1:]

    def split_off_bencoded_string(self, bencoded_list):
        first_colon_index = bencoded_list.find(b":")
        end_of_string = 1 + first_colon_index + int(bencoded_list[:first_colon_index])
        return bencoded_list[:end_of_string], bencoded_list[end_of_string:]

    def split_bencoded_list(self, bencoded_list, depth=0):
        elements = []

        while len(bencoded_list) > 0:
            bencoded_type = BencodedTypes().get_bencoded_type(bencoded_list)

            if bencoded_type == BencodedTypes.INTEGER:
                element, bencoded_list = self.split_off_bencoded_integer(bencoded_list)
                elements.append(element)

            elif bencoded_type == BencodedTypes.STRING:

                element, bencoded_list = self.split_off_bencoded_string(bencoded_list)

                elements.append(element)

            elif bencoded_type == BencodedTypes.LIST:
                bencoded_list = bencoded_list[1:]
                element, bencoded_list = self.split_bencoded_list(bencoded_list, depth + 1)
                elements.append(element)

            elif bencoded_type == BencodedTypes.END_OF_LIST:
                return elements, bencoded_list[1:]

            if depth == 0:
                break

        if depth == 0:
            return elements[0], b""

        return elements, b""

    def split_dict_keys_and_values(self, bencoded_dictionary, depth=0):

        dict_key, bencoded_dictionary = self.TYPE_TO_SPLITTER_MAP[
            BencodedTypes().get_bencoded_type(bencoded_dictionary)](bencoded_dictionary)

        dict_value, bencoded_dictionary = self.TYPE_TO_SPLITTER_MAP[
            BencodedTypes().get_bencoded_type(bencoded_dictionary)](bencoded_dictionary)

        return dict_key, dict_value, bencoded_dictionary

    def split_bencoded_dictionary(self, bencoded_dictionary, depth=0):
        result = {}

        while len(bencoded_dictionary) > 2:
            bencoded_type = BencodedTypes().get_bencoded_type(bencoded_dictionary)

            if bencoded_type == BencodedTypes.DICT:
                bencoded_dictionary = bencoded_dictionary[1:]
                while bencoded_type != BencodedTypes.END_OF_LIST:

                    k, v, bencoded_dictionary = self.split_dict_keys_and_values(bencoded_dictionary)
                    result[k] = v

                    if bencoded_dictionary != b'':
                        bencoded_type = BencodedTypes().get_bencoded_type(bencoded_dictionary)

                    else:
                        break

                bencoded_dictionary = bencoded_dictionary[1:]

        return result, b''
