text = '-c send:text -ip "192.168.1.8" -port "80" -content "Hello Cindy"'

class Parser():
    def __init__(self):
        self.state = "parameter"
        self.state_func = self.parameter_state
        self.states = ["command","parameter","text","end"]

        self.global_text = ""
        self.double_quotations_num = 0

    def reset(self):
        self.state = "parameter"
        self.global_text = ""
        self.double_quotations_num = 0

    def appendGlobalText(self, text, override):
        if text == " " and not override:
            return;
        self.global_text += text

    def transition(self, current_state, next_state):
        if current_state == next_state:
            return None;

        text = self.global_text
        self.state = next_state

        match self.state:
            case "parameter":
                self.state_func = self.parameter_state
            case "command":
                self.state_func = self.command_state
            case "text":
                self.state_func = self.text_state

        self.global_text = ""
        self.double_quotations_num = 0

        return text
    
    def end_state(self):
        # print(self.global_text)
        pass

    def parameter_state(self, text, end):
        if end:
            self.appendGlobalText(text=text, override=False)
            self.end_state()
            return self.global_text
        
        if text == " ":
            match self.global_text:
                case "-c":
                    return self.transition(current_state="parameter", next_state="command")
                case _:
                    if self.global_text.strip() == "":
                        return;
                
                    data = self.transition(current_state="parameter", next_state="text")
                    return data
                
        if text != '"':
            self.appendGlobalText(text=text, override=False)

        return None


    def command_state(self, text, end):
        if end:
            self.appendGlobalText(text=text, override=False)
            data = self.transition(current_state="command", next_state="parameter")

            return data
        
        if text == " ":
            data = self.transition(current_state="command", next_state="parameter")

            return data
        
        self.appendGlobalText(text=text, override=False)

        return None

    def text_state(self, text, end):
        if end:
            self.appendGlobalText(text=text, override=True)
            self.end_state()

            data = self.transition(current_state="text", next_state="parameter")

            if data is not None:
                
                return data+'"'
            return None
        
        if text == '"':
            if self.double_quotations_num > 0:
                data = self.transition(current_state="text", next_state="parameter")

                if data is not None:
                    
                    return data+'"'
            else:
                self.double_quotations_num += 1

        self.appendGlobalText(text=text, override=True)

        return None
    
    def parse(self,text):
        self.reset()

        commands_array = []
        index = 0
        for content in text:
            data = None
            if index == len(text)-1:
                data = self.state_func(content, True)
            else:
                data = self.state_func(content, False)


            if data is not None:
                commands_array.append({"index":index, "content": data})

            index += 1

        commands_array_length = len(commands_array)

        if commands_array_length%2:
            raise Exception("Incomplete command")
        
        indexes = []
        i = 0
        for command in commands_array:
            if command["content"] == "-c":
                indexes.append(i)
            i += 1
        
        pairs = []
        indexes_length = len(indexes)

        for x in range(0, len(indexes)):
            index = indexes[x]

            if x == indexes_length-1:
                pairs.append((index,None))
            else:
                pairs.append((index, indexes[x+1]-1))

        syntax_array = []

        for pair in pairs:
            start_index, end_index = pair

            if start_index is None:
                start_index = commands_array_length-1
            
            if end_index is None:
                end_index = commands_array_length-1

            data = {
                "root_command":None,
                "parameters": []
            }

            for x in range(start_index,end_index, 2):

                value_1 = commands_array[x]
                value_2 = commands_array[x+1]

                match value_1["content"]:
                    case "-c":
                        data["root_command"] = {"param":value_1, "value":value_2}
                    case _:
                        data["parameters"].append({"param":value_1,"value":value_2})
            
            syntax_array.append(data)

        self.reset()

        return syntax_array          


# parser_1 = Parser();

# parser_1.parse(text)
    