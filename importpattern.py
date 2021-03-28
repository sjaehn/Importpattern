import copy
import sys
import os
import re
import glob

bpm = 90.0
accent = 1.5


class Parameter:
    def __init__(self, symbol, value, min, max, typ="str", func=None):
        self.symbol = symbol
        self.value = value
        self.min = min
        self.max = max
        self.typ = typ
        self.func = func

    def set(self, value):
        if self.typ == "float":
            try:
                f = float(value)
                if (f >= self.min) and (f <= self.max):
                    self.value = f
                else:
                    print("Invalid parameter for", self.symbol)
                    return
            except ValueError:
                print("Invalid parameter for", self.symbol)
                return

        elif self.typ == "int":
            try:
                i = int(value)
                if (i >= self.min) and (i <= self.max):
                    self.value = i
                else:
                    print("Invalid parameter for", self.symbol)
                    return
            except ValueError:
                print("Invalid parameter for", self.symbol)
                return
        else:
            self.value = value

        if self.func is not None:
            x = self.value
            exec(self.func)


parameters = [Parameter("bps", 1.5, 1.0 / 60.0, 5.0, "float", "global bpm; bpm = 60.0 * x"),
              Parameter("prefix", "", 0, 0, "str"),
              Parameter("channel", 10, 1, 16, "int"),
              Parameter("velocity", 1.0, 0.0, 2.0, "float"),
              Parameter("accent", 1.5, 0.0, 2.0, "float", "global accent; accent = x"),
              Parameter("mode", 1, 1, 3, "int"),
              Parameter("on_key", 0, 0, 2, "int")
              ]


def get_parameter(symbol):
    symbol_id = next((i for i in range(len(parameters)) if parameters[i].symbol == symbol), None)
    if symbol_id is not None:
        return parameters[symbol_id].value
    else:
        return None


class Instrument:
    def __init__(self, symbol, name, code, data):
        self.symbol = symbol
        self.name = name
        self.code = code
        self.data = data


instruments = [Instrument("ab", "Ac. Bass", 35, []),
               Instrument("bd", "Bass Drum", 36, []),
               Instrument("sn", "Snare", 38, []),
               Instrument("es", "E-Snare", 40, []),
               Instrument("rm", "Stick", 37, []),
               Instrument("cp", "Clap", 39, []),
               Instrument("ft", "Low FTom", 41, []),
               Instrument("lt", "Low Tom", 43, []),
               Instrument("ft", "Floor Tom", 45, []),
               Instrument("mt", "Mid Tom", 47, []),
               Instrument("hm", "HiMid Tom", 48, []),
               Instrument("ht", "Hi Tom", 50, []),
               Instrument("ch", "Closed HH", 42, []),
               Instrument("hh", "Pedal HH", 44, []),
               Instrument("oh", "Open HH", 46, []),
               Instrument("cr", "Crash", 49, []),
               Instrument("ri", "Ride", 51, []),
               Instrument("cy", "Cymbal", 52, []),
               Instrument("be", "Bell", 53, []),
               Instrument("ta", "Tambourine", 54, []),
               Instrument("sc", "Splash", 55, []),
               Instrument("cb", "Cowbell", 56, []),
               Instrument("cs", "Crash 2", 57, []),
               Instrument("vi", "Vibra slap", 58, []),
               Instrument("rc", "Ride 2", 59, []),
               Instrument("hb", "Hi Bongo", 60, []),
               Instrument("lb", "Low Bongo", 61, []),
               Instrument("mh", "MH Conga", 62, []),
               Instrument("hc", "OH Conga", 63, []),
               Instrument("lc", "Low Conga", 64, []),
               Instrument("he", "H Timbale", 65, []),
               Instrument("le", "L Timbale", 66, []),
               Instrument("ag", "H Agogo", 67, []),
               Instrument("la", "L Agogo", 68, []),
               Instrument("ca", "Cabasa", 69, []),
               Instrument("ma", "Maracas", 70, []),
               Instrument("sw", "Sh. Whistle", 71, []),
               Instrument("lw", "Ln. Whistle", 72, []),
               Instrument("sg", "Sh. Guiro", 73, []),
               Instrument("lg", "Ln. Guiro", 74, []),
               Instrument("cl", "Claves", 75, []),
               Instrument("hi", "Hi Wood", 76, []),
               Instrument("li", "Low Wood", 77, []),
               Instrument("mc", "Mt. Cuica", 78, []),
               Instrument("oc", "Op. Cuica", 79, []),
               Instrument("tr", "Mt. Triangle", 80, []),
               Instrument("ot", "Op. Triangle", 81, [])
               ]


class Preset:
    def __init__(self, project_name, target_dir, lines):
        self.project = project_name
        self.bpm = bpm
        self.beats_per_bar = None
        self.nr_of_steps = None
        self.steps_per_beat = None
        self.target = target_dir
        self.instruments = copy.deepcopy(instruments)
        self.active_instruments = []
        self.ac = []
        self.pattern = []

        # Parse lines
        for line in lines:
            p = parse_line(line)
            if p is not None:

                if p[0] == "bps":
                    try:
                        val = float(p[1])
                        self.bpm = val * 60.0
                    except ValueError:
                        print("Invalid value for bps for", self.project)

                elif p[0] == "ac":
                    if self.beats_per_bar is None:
                        self.beats_per_bar = get_beats(line)

                    if self.nr_of_steps is None:
                        self.nr_of_steps = get_steps(line)

                    if self.steps_per_beat is None:
                        self.steps_per_beat = get_steps_per(line)

                    self.ac = []
                    for c in p[1]:
                        if c == '0':
                            self.ac.append(1)
                        else:
                            self.ac.append(accent)

                else:
                    for i in range(len(instruments)):
                        if p[0] == self.instruments[i].symbol:
                            if self.beats_per_bar is None:
                                self.beats_per_bar = get_beats(line)

                            if self.nr_of_steps is None:
                                self.nr_of_steps = get_steps(line)

                            if self.steps_per_beat is None:
                                self.steps_per_beat = get_steps_per(line)

                            pattern = []
                            for c in p[1]:
                                if c == '0':
                                    pattern.append(0)
                                else:
                                    pattern.append(1)

                            self.instruments[i].data = pattern
                            break

        # Set active instruments
        for i in self.instruments:
            if i.data:
                self.active_instruments.append(i)

        if len(self.active_instruments) > 16:
            print("Too many instruments in", project_name)
            return

        # Make pattern
        if (self.nr_of_steps is None) or (self.steps_per_beat is None):
            print("No data to create preset for", project_name)
            return

        else:
            size = (int((self.nr_of_steps - 1) / 8) + 1) * 8
            self.beats_per_bar = int(size / self.steps_per_beat)

            if (size < 8) or (size > 32):
                print("Invalid pattern size in", project_name)
                return

            self.pattern = []
            for step in range(0, size):
                for row in range(len(self.active_instruments)):
                    if step < len(self.active_instruments[row].data):
                        if self.active_instruments[row].data[step] == 1:
                            if len(self.ac) <= step:
                                ve = self.active_instruments[row].data[step]
                            else:
                                ve = self.active_instruments[row].data[step] * self.ac[step]
                            self.pattern.append("id:" + str(step * 16 + row) + "; ch:1; st:0; oc:0; ve:" +
                                                "{:.2f}".format(ve) + "; du:1,00; rg:1; rs:0; ro:0; rv:0,00; rd:0,00;")
                    else:
                        self.pattern.append("id:" + str(step * 16 + row) +
                                            "; ch:112; st:0; oc:0; ve:0,00; du:1,00; rg:1; rs:0; ro:0; rv:0,00; rd:0,"
                                            "00;")

    def make_manifest(self, filename):
        lines = read_file(filename)
        for i in range(len(lines)):
            lines[i] = lines[i].replace("@@project_name@@", self.project)
        return lines

    def make_preset(self, filename):
        instrument_codes = ""
        instrument_names = ""
        count = len(self.active_instruments)
        for i in range(0, 16):
            if i < count:
                instrument_codes += str(self.active_instruments[i].code + 256) + "; "
                instrument_names += "\"" + self.active_instruments[i].name + "\"; "

        for inst in self.instruments:
            if count >= 16:
                break

            overlaps = [o for o in self.active_instruments if o.code == inst.code]
            if not overlaps:
                instrument_codes += str(inst.code + 256) + "; "
                instrument_names += "\"" + inst.name + "\"; "
                count = count + 1

        lines = read_file(filename)

        pattern_pos = lines.index("@@pattern@@")
        lines.remove("@@pattern@@")
        for i in range(0, len(self.pattern)):
            lines.insert(pattern_pos + i, self.pattern[i])

        for i in range(len(lines)):
            if lines[i].find("@@") >= 0:
                lines[i] = lines[i].replace("@@project_name@@", self.project)
                lines[i] = lines[i].replace("@@nr_of_steps@@", "{:.1f}".format(self.nr_of_steps))
                lines[i] = lines[i].replace("@@beats_per_bar@@", "{:.1f}".format(self.beats_per_bar))
                lines[i] = lines[i].replace("@@steps_per_beat@@", "{:.1f}".format(self.steps_per_beat))
                lines[i] = lines[i].replace("@@bpm@@", "{:.1f}".format(self.bpm))
                lines[i] = lines[i].replace("@@channel@@", "{:.1f}".format(get_parameter("channel")))
                lines[i] = lines[i].replace("@@velocity@@", "{:.1f}".format(get_parameter("velocity")))
                lines[i] = lines[i].replace("@@mode@@", "{:.1f}".format(get_parameter("mode")))
                lines[i] = lines[i].replace("@@on_key@@", "{:.1f}".format(get_parameter("on_key")))
                lines[i] = lines[i].replace("@@instrument_codes@@", instrument_codes)
                lines[i] = lines[i].replace("@@instrument_names@@", instrument_names)
        return lines


def read_file(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    file.close()
    return lines


def write_file(filename, lines):
    with open(filename, 'w') as file:
        file.write('\n'.join(lines))
    file.close()


def parse_pattern(rawtext):
    text = rawtext.replace(" ", "")
    p1 = text.find("\"")

    text = text[p1 + 1:]
    p2 = text.find("\"")

    if (p1 < 0) or (p2 < 0):
        print("Can't parse pattern: Invalid pattern containing", rawtext)
        return

    text = text[:p2]
    text = re.sub('[^~t]+', '', text)
    text = text.replace("~", "0")
    text = text.replace("t", "1")
    return text


def get_steps(line):
    text = line.replace(" ", "")
    p1 = text.find("\"")

    text = text[p1 + 1:]
    p2 = text.find("\"")

    if (p1 < 0) or (p2 < 0):
        print("Can't parse pattern: Invalid pattern containing", line)
        return

    text = text[:p2]
    text = re.sub('[^~t]+', '', text)
    return len(text)


def get_beats(line):
    text = line.replace(" ", "")
    p1 = text.find("\"")

    text = text[p1 + 1:]
    p2 = text.find("\"")

    if (p1 < 0) or (p2 < 0):
        print("Can't parse pattern: Invalid pattern containing", line)
        return

    text = text[:p2]
    return text.count('[')


def get_steps_per(line):
    text = line.replace(" ", "")
    p1 = text.find("\"")

    text = text[p1 + 1:]
    p2 = text.find("\"")

    if (p1 < 0) or (p2 < 0):
        print("Can't parse pattern: Invalid pattern containing", line)
        return

    text = text[:p2]

    p3 = text.find('[')
    text = text[p3 + 1:]
    p4 = text.find(']')
    text = text[:p4]

    return len(text)


def parse_line(line):
    eq_pos = line.find("=")
    if eq_pos > 0:
        left_side = line[:eq_pos].replace(" ", "")
        right_side = line[eq_pos + 1:]

        if left_side == "bps":
            return ["bps", right_side]

        if left_side == "ac":
            return ["ac", parse_pattern(right_side)]

        for i in instruments:
            if i.symbol == left_side:
                return [i.symbol, parse_pattern(right_side)]

        print("Ignore unknown symbol", left_side)

    else:
        return


def print_help():
    print("Usage: python importpattern.py [options] [parameters] source_file [target_dir]")
    print("")
    print("Options:")
    print("    -h, --help      Print this help message")
    print("")
    print("Parameters:")
    print("    Format: symbol=value")
    print("    Symbols:")
    print("        prefix      Prefix added to the target name")
    print("        bps         Beats per second (default=1.5)")
    print("        channel     Midi channel(default=10)")
    print("        velocity    MIDI note velocity factor(default=1.0)")
    print("        accent      Factor for accented notes(default=1.5)")
    print("        mode        1 = autoplay, 2 = host & MIDI controlled, ")
    print("                    3 = host controlled(default=1)")
    print("        on_key      Option for MIDI controlled mode.0 = Restart, ")
    print("                    1 = restart and sync, 2 = continue (default=0)")
    print("        ab,bd,...   Re-assign instrument symbols to a new code or a new name")


def main():
    source_names = None
    target = ""

    for arg in sys.argv[1:]:
        arg_str = str(arg)

        if (arg_str == "-h") or (arg_str == "--help"):
            print_help()
            return

        param = False
        ep = arg_str.find("=")
        if ep > 0:
            ls = arg_str[:ep]
            rs = arg_str[ep + 1:]

            symbol_id = next((i for i in range(len(parameters)) if parameters[i].symbol == ls), None)
            if symbol_id is not None:
                parameters[symbol_id].set(rs)
                param = True

            else:
                for i in range(len(instruments)):
                    if ls == instruments[i].symbol:
                        if rs.isdigit():
                            try:
                                instruments[i].code = int(rs)
                            except ValueError:
                                print("Invalid value for", ls)
                        else:
                            instruments[i].name = rs
                        param = True
                        break

        if param is False:
            if source_names is None:
                source_names = glob.glob(arg_str)

            else:
                target = arg_str

    if source_names is None:
        print_help()
        return

    for source_name in source_names:
        project_name = get_parameter("prefix") + os.path.splitext(os.path.basename(source_name))[0]
        target_path = target
        if target_path != "":
            target_path += "/"
        target_path += "B.SEQuencer_" + project_name + ".lv2"

        # Read and parse source file
        print("Read", source_name)
        lines = read_file(source_name)
        preset = Preset(project_name, target_path, lines)
        if (preset.beats_per_bar is None) or (preset.nr_of_steps is None) or (preset.steps_per_beat is None) or (
                not preset.pattern):
            print("")
            continue

        # Write
        print("Create", project_name)
        if not os.path.exists(target_path):
            os.mkdir(target_path)

        py_dir = os.path.dirname(os.path.abspath(__file__))

        print("Write manifest.ttl")
        manifest = preset.make_manifest(py_dir + "/Template.lv2/manifest.ttl")
        write_file(target_path + "/manifest.ttl", manifest)

        print("Write", project_name + ".ttl")
        ttl = preset.make_preset(py_dir + "/Template.lv2/project_name.ttl")
        write_file(target_path + "/" + project_name + ".ttl", ttl)
        print("")


if __name__ == "__main__":
    main()
