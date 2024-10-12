import json
from splitter import Splitter
from converter import Converter
from bencoded_types import BencodedTypes


class Decoder:
    def __init__(self):
        self.bencoded_types = BencodedTypes()  # Add this line
        self.TYPE_TO_DECODER_MAP = {
            BencodedTypes.STRING: self.decode_bencoded_string,
            BencodedTypes.INTEGER: self.decode_bencoded_integer,
            BencodedTypes.LIST: self.decode_bencoded_list,
            BencodedTypes.DICT: self.decode_bencoded_dictionary,
        }
        self.splitter = Splitter()
        self.converter = Converter()

    def decode_bencoded_string(self, bencoded_value):
        first_colon_index = bencoded_value.find(b":")

        if first_colon_index == -1:
            raise ValueError("Invalid encoded string value")

        return bencoded_value[1 + first_colon_index: 1 + first_colon_index + int(bencoded_value[:first_colon_index])]

    def decode_bencoded_integer(self, bencoded_value):
        end_index = bencoded_value.find(b"e")

        if end_index == -1:
            raise ValueError("Invalid encoded integer value")

        return bencoded_value[1:end_index]

    def decode_bencoded_list_elements(self, bencoded_split_list):
        decoded_elements = []

        for bv in bencoded_split_list:
            if isinstance(bv, list):
                decoded_elements.append(self.decode_bencoded_list_elements(bv))

            else:
                decoded_elements.append(self.TYPE_TO_DECODER_MAP[self.bencoded_types.get_bencoded_type(bv)](bv))

        return decoded_elements

    def decode_bencoded_list(self, bencoded_list):
        split_bencoded_values, _ = self.splitter.split_bencoded_list(bencoded_list)
        return self.decode_bencoded_list_elements(split_bencoded_values)

    def decode_bencoded_dict_elements(self, bencoded_split_dict):
        result = {}

        for k, v in bencoded_split_dict.items():
            k = self.converter.convert_decoded_integer_and_string_bytes(self.decode_bencoded_string(k))
            if isinstance(v, dict):
                v = self.decode_bencoded_dict_elements(v)

            elif isinstance(v, list):
                v = self.decode_bencoded_list_elements(v)

            else:
                v = self.TYPE_TO_DECODER_MAP[self.bencoded_types.get_bencoded_type(v)](v)

            result[k] = v
        return result

    def decode_bencoded_dictionary(self, bencoded_dictionary):
        bencoded_split_dict, _ = self.splitter.split_bencoded_dictionary(bencoded_dictionary)
        return self.decode_bencoded_dict_elements(bencoded_split_dict)

    def decode_bencode(self, bencoded_value):
        try:
            return self.TYPE_TO_DECODER_MAP[self.bencoded_types.get_bencoded_type(bencoded_value)](bencoded_value)

        except ValueError as e:
            print(f"Error during decoding with message: {e}")

        except KeyError as e:
            print(f"Unsupported type of decoder with mesage : {e}")

        raise NotImplementedError(
            f"Given type of bencoded string not supported: {bencoded_value}")

    def decode_bencoded_value(self, bencoded_value):
        return json.loads(json.dumps(self.decode_bencode(bencoded_value), default=self.converter.convert_decoded_bytes))
