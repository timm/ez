# <!-- vim: set ts=2 sw=2 sts=2 et: -->
"""
## Ezr.py
&copy;  2024 Tim Menzies (timm@ieee.org). BSD-2 license

### USAGE:

python3 ezr.py [OPTIONS]

This code explores multi-objective optimization; i.e. what
predicts for the better goal values? This code also explores
active learning; i.e. how to make predictions after looking at
the fewest number of goal values?

### OPTIONS:

    -b --buffer int    chunk size, when streaming   = 100
    -B --branch bool   set branch method            = False
    -d --divide int    half with mean or median     = 0
    -D --Dull   bool   if true, round to cohen's d  = False
    -L --Last   int    max number of labels         = 30
    -c --cut    float  borderline best:rest         = 0.5
    -C --Cohen  float  pragmatically small          = 0.35
    -e --eg     str    start up action              = mqs
    -f --fars   int    number of times to look far  = 20
    -h --help          show help                    = False
    -i --iter   int    length of done minus label   = 0
    -k --k      int    low frequency Bayes hack     = 1
    -l --label  int    initial number of labels     = 4
    -m --m      int    low frequency Bayes hack     = 2
    -p --p      int    distance formula exponent    = 2
    -s --seed   int    random number seed           = 1234567891
    -S --Stop   int    min size of tree leaves      = 30
    -t --train  str    training csv file. row1 has names = data/misc/auto93.csv

### Data File Format

Training data consists of csv files where "?" denotes missing values.
Row one  list the columns names, defining the roles of the columns:

- NUMeric column names start with an upper case letter.
- All other columns are SYMbolic.
- Names ending with "+" or "-" are goals to maximize/minimize
- Anything ending in "X" is a column we should ignore.

For example, here is data where the goals are `Lbs-,Acc+,Mpg+`
i.e. we want to minimize car weight and maximize acceleration
and maximize fuel consumption.

     Clndrs   Volume  HpX  Model  origin  Lbs-  Acc+  Mpg+
     -------  ------  ---  -----  ------  ----  ----  ----
      4       90      48   78     2       1985  21.4   40
      4       98      79   76     1       2255  17.7   30
      4       98      68   77     3       2045  18.6   30
      4       79      67   74     2       2000  16     30
      ...
      4      151      85   78     1       2855  17.6   20
      6      168      132  80     3       2910  11.4   30
      8      350      165  72     1       4274  12     10
      8      304      150  73     1       3672  11.5   10

Note that the top rows are
better than the bottom ones (lighter, faster cars that are
more economical).
"""
import lib
import re,sys

class SETTINGS:
  def __init__(self,s:str) -> None:
    "Make one slot for any line  `--slot ... = value`"
    self._help = s
    want = r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)"
    for m in re.finditer(want,s): self.__dict__[m[1]] = lib.coerce(m[2])
    self.sideEffects()

  def __repr__(self) -> str:
    "hide secret slots (those starting with '_'"
    return str({k:v for k,v in self.__dict__.items() if k[0] != "_"})

  def cli(self):
    "Update slots from command-line"
    d = self.__dict__
    for k,v in d.items():
      v = str(v)
      for c,arg in enumerate(sys.argv):
        after = sys.argv[c+1] if c < len(sys.argv) - 1 else ""
        if arg in ["-"+k[0], "--"+k]:
          d[k] = coerce("False" if v=="True" else ("True" if v=="False" else after))
    self.sideEffects()

  def sideEffects(self):
    "Run side-effects."
    d = self.__dict__
    random.seed(d.get("seed",1))
    if d.get("help",False):
      sys.exit(print(self._help))
