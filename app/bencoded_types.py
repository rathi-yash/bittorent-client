class BencodedTypes:
    STRING = "string"
    INTEGER = "integer"
    LIST = "list"
    END_OF_LIST = "end_of_list"
    DICT = "dictionary"

    @staticmethod
    def get_bencoded_type(bencoded_value):
        if not isinstance(bencoded_value, bytes):
            raise TypeError(f"Bencoded value should be of type bytes, instead got : {type(bencoded_value)}")

        first_char = chr(bencoded_value[0])

        if first_char.isdigit():
            return BencodedTypes.STRING
        elif first_char == "i":
            return BencodedTypes.INTEGER
        elif first_char == "l":
            return BencodedTypes.LIST
        elif first_char == "e":
            return BencodedTypes.END_OF_LIST
        elif first_char == "d":
            return BencodedTypes.DICT

        raise ValueError(f"Unsupported bencoded value type {bencoded_value}")
