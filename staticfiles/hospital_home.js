// Counter Animation
function animateCounter(id, target) {
  let counter = document.getElementById(id);
  let count = 0;
  let speed = target / 100;
  let interval = setInterval(() => {
    count += speed;
    if (count >= target) {
      count = target;
      clearInterval(interval);
    }
    counter.innerText = Math.floor(count);
  }, 30);
}

// Example numbers
animateCounter("doctors", 40);
animateCounter("patients", 350);
animateCounter("departments", 12);
animateCounter("appointments", 150);
