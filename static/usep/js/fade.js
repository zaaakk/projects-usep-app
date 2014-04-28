function fade(behavior, element) {
  console.log("fade!");

  var fadeInCondition = function(op) { return op >= 0.25; }
  var fadeInIncrement = function(op) { return op + (op * 0.1); }
  var fadeOutCondition = function(op) { return op <= 0.1; }
  var fadeOutDecrement = function(op) { return op - (op * 0.1); }
  
  var op = 0.1;  // initial opacity
  if (behavior === "out") {
    op = 0.3; 
  }

  var timer = setInterval(function () {
      console.log("fading with op " + op + "!");
      if (behavior === "in"){
        if (fadeInCondition(op)) {
          console.log("stop fade in!");
          clearInterval(timer);
          element.style.display = 'visible';  
        }
        
        op = fadeInIncrement(op);
        console.log('op: ' + op);  

      }
      else if (behavior === "out") {
        if (fadeOutCondition(op)) {
          console.log("stop fade out!");
          clearInterval(timer);
          element.style.display = 'none';  
        }
        
        op = fadeOutDecrement(op); 
        console.log('op: ' + op); 

      }
      element.style.opacity = op;
      element.style.filter = 'alpha(opacity=' + op * 100 + ")";
      
  }, 20);
}