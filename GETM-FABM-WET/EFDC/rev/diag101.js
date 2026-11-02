'use strict';
setTimeout(function(){
  var ms=Process.enumerateModules();
  var names=ms.map(function(m){return m.name;}).filter(function(n){return /fnp|flex|lmg|act_|dsilic|clr|mscor|winhttp|wininet/i.test(n);});
  send('MODULES: '+names.join(', '));
  send('TOTAL '+ms.length);
}, 4000);
send('ready');
