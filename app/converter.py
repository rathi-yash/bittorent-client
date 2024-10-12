class Converter:

    def convert_decoded_integer_and_string_bytes(self, data):
        potential_str = data.decode('utf-8', errors='ignore')
        if potential_str.isdecimal() or potential_str[1:].isdecimal():
            return int(potential_str)
        else:
            return potential_str

    def convert_decoded_bytes(self, data: bytes):
        if isinstance(data, bytes):
            return self.convert_decoded_integer_and_string_bytes(data)

        elif isinstance(data, list):
            result = []
            for element in data:
                result.append(self.convert_decoded_bytes(element))
            return result

        elif isinstance(data, dict):

            result = {}
            for k, v in data.items():
                k = self.convert_decoded_bytes(k)
                v = self.convert_decoded_bytes(v)
                result[k] = v
            return result

        raise TypeError(f"Type not serializable: {type(data)}")
