
$1 | gawk '
  match($0,"^@@ -([0-9]+),([0-9]+) [+]([0-9]+),([0-9]+) @@",a){
    left=a[1]
    ll=length(a[2])
    right=a[3]
    rl=length(a[4])
  }
  /^(---|\+\+\+|[^-+ ])/{ print;next }
  { line=substr($0,2) }
  /^[-]/{ printf "-%"ll"s %"rl"s:%s\n",left++,""     ,line;next }
  /^[+]/{ printf "+%"ll"s %"rl"s:%s\n",""    ,right++,line;next }
        { printf " %"ll"s %"rl"s:%s\n",left++,right++,line }
'