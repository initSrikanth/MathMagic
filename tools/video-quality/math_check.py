"""Independent exact arithmetic on authored worked expressions; unsupported language is reported."""
import ast,re
from fractions import Fraction
OPS={ast.Add:lambda a,b:a+b,ast.Sub:lambda a,b:a-b,ast.Mult:lambda a,b:a*b,ast.Div:lambda a,b:a/b}
def value(n):
 if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)):return Fraction(str(n.value))
 if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):return value(n.operand)*(1 if isinstance(n.op,ast.UAdd) else -1)
 if isinstance(n,ast.BinOp) and type(n.op) in OPS:return OPS[type(n.op)](value(n.left),value(n.right))
 raise ValueError('Unsupported expression')
def expression(s):return value(ast.parse(s.strip(),mode='eval').body)
def equation_ok(s):
 s=s.replace('×','*').replace('÷','/').replace('−','-').replace(',','');s=s.split(':')[-1].strip();s=re.sub(r'(\d+(?:\.\d+)?)%',r'(\1/100)',s)
 if '=' not in s or any(x in s for x in ['?','≠','<','>','≈']):return None
 a,b=s.split('=',1);b=re.sub(r'\s+(?:cm|m|g|kg|L|mL|books|tiles|square units|square metres|square centimetres)(?:²)?\s*$','',b)
 try:return expression(a)==expression(b)
 except (ValueError,SyntaxError,ZeroDivisionError):return None

def inspect(script):
 checked=0;unsupported=[]
 for cue in script.get('beats',[]):
  for line in cue.get('board',[]):
   result=equation_ok(line)
   if result is False and not cue.get('intentional_error'):raise AssertionError('Incorrect worked equation without explicit misconception annotation: '+line)
   if result is not None:checked+=1
   elif '=' in line:unsupported.append(line)
 return {'exact_equations_checked':checked,'unsupported_requires_review':unsupported,'note':'This does not certify rendered models, spoken mathematics or curriculum coverage.'}
