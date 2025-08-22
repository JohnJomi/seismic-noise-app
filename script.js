// Example: Animate process list items one by one
document.addEventListener("DOMContentLoaded", () => {
  const items = document.querySelectorAll(".process-list li");
  items.forEach((li, index) => {
    li.style.opacity = 0;
    setTimeout(() => {
      li.style.transition = "opacity 0.8s ease, transform 0.8s ease";
      li.style.opacity = 1;
      li.style.transform = "translateX(0)";
    }, 500 + index * 400);
  });
});
