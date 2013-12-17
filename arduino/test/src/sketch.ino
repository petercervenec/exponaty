// Commands
//  b  set mode to binary, returns one AD value
//  d  set mode to decimal, returnd one AD value
//  r  reset to default - binary mode – nerobí nič rozumné...
//  s  Start/Stop turns on/off continuous stream od AD values
//            Binary mode: 16 bit value high byte first. AD is 10 bit only.
//            Decadic mode: Ascii value + line end.

int mode;  // 0 binary (default), 1 decimal,
int AnalogValue;
volatile int newvalue;
volatile int running;

void setup()
{
  mode=0;
  newvalue=0;
  running=0;
  cli();
  TCCR1A=0;
  TCCR1B=0;
  OCR1A=4000;
  TCCR1B|=(1<<CS10|1<<WGM12);
  TIMSK1|=(1<<OCIE1A); 
  sei();   
  Serial.begin(9600);  
}

void loop()

{
  byte b;
  if (newvalue==1)
  {
    PrintValue(AnalogValue);
    newvalue=0;
  }

  if (Serial.available()>0) {
      b=Serial.read();

      if (b=='b')
      {
       mode=mode&254;
       int value=analogRead(A0);
       PrintValue(value); 
      }

      if (b=='d')
      {
        mode=mode|1;
        int value=analogRead(A0);
        PrintValue(value); 
      }   

      if (b=='r')
      {
        mode=0;
	running=0;
	newvalue=0;
        Serial.println("System reset to default");
      }

      if (b=='s')
      {
       if (running==1) running=0;
       else running=1;       
      }
    }
}

void PrintValue(int value)
{
  if ((mode&1)==1)  // decimal mode
  {
    Serial.println(value);
  } else {
    byte high=(byte)((value>>8)&255);
    byte low=(byte)(value&255);
    Serial.write(high);
    Serial.write(low);
  }
}

ISR(TIMER1_COMPA_vect)
{
  AnalogValue=analogRead(A0);
  if (running==1)
    newvalue=1;
  else
    newvalue=0;
}  


