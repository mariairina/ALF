PARSER_BEGIN(Sick)

public class Sick{
	
    public static void main(String[] args) throws ParseException, Exception
	{
	try {
        Sick start = new Beah(System.in);
		while (true)
			{ start.Verif2();
			System.out.println("<(\")happy!"); System.exit(-1);}
		}
		
	catch(ParseException e)
		{
			System.out.println(e.getMessage());
			System.out.println("\t (\'^\')mad!!! He doesn't understand the language!"); }
		}
		
    }


PARSER_END(Beah)

SKIP:  { " "|"\t" | "\r"  }
                
TOKEN: { <#NUMBER: (("-")? <INT>) | (("-")? <INT> "." <INT>)| <ZERO> >}
TOKEN: { <VARIABLE: (<ID>)+ >}
TOKEN: { <TERM: (<ID>)+|<NUMBER> >}
TOKEN: {<#INT: (["0"-"9"])+ >}
TOKEN: {<#ZERO: "0" >}
TOKEN: {<#ID: ["a"-"z","A"-"Z"]> }
TOKEN: {<TERMINATOR: "<(^)">}
TOKEN: {<EOP: "('^')">}
TOKEN: {< EOL: ("\n")? >}
TOKEN : 
{ 
	  <ASSIGN : "=">  
	| <PLUS : "+" >  
	| <MINUS:"-"> 
	| <MULTIPLY:"*"> 
	| <DIVIDE:"/"> 
	
}

TOKEN:
{
	  <EQUAL: "==" > 
	| <LESSEQUAL: "<=" > 
	| <LESS: "<" > 
	| <GREATEREQUAL: ">=" > 
	| <GREATER: ">" > 
	| <DIFFERENT: "!=" > 
	
}


void Verif():
{}
{
< VARIABLE >< ASSIGN >(<TERM>)(( <PLUS> | <MINUS> | <MULTIPLY> | <DIVIDE> )(<TERM>))?<TERMINATOR>
}

void Verif2():

{Token t=null;
int i;
int value=0;}
{
((< VARIABLE > < ASSIGN >
t=<TERM>
{i=Integer.parseInt(t.image); }
{value=i; }
(
 <PLUS> 
 t=<TERM>
 {i=Integer.parseInt(t.image); }
 {value+=i; }
 
 |
 <MINUS>
 t=<TERM>
 {i=Integer.parseInt(t.image); }
 {value-=i; }
 
 |
 <MULTIPLY>
 t=<TERM>
 {i=Integer.parseInt(t.image); }
 {value*=i; }

 |
 <DIVIDE>
 t=<TERM>
 {i=Integer.parseInt(t.image); }
 {value/=i; }
 
 )* <TERMINATOR> {System.out.println(value);} <EOL>)*)
 (<EOL>)* 
 <EOP>

}


/* Input:
a=4+7 <(^)
b=6*7 <(^)
c=5/3 <(^)
('^')
*/
