# <!-- vim: set ts=2 sw=2 sts=2 et: -->
from fileinput import FileInput as file_or_stdin

def coerce(s:str) -> atom:
  "Coerces strings to atoms."
  try: return ast.literal_eval(s)
  except Exception:  return s

def csv(file) -> Generator[row]:
  "Iteratively return rows in a csv"
  infile = sys.stdin if file=="-" else open(file)
  with infile as src:
    for line in src:
      line = re.sub(r'([\n\t\r ]|#.*)', '', line)
      if line: yield [coerce(s.strip()) for s in line.split(",")]

def dot(s:str=".") -> None: 
  "print a character to standard error"
  print(s, file=sys.stderr, flush=True, end="")

def timing(fun) -> number:
  "Return time to run a function."
  start = time()
  fun()
  return time() - start
