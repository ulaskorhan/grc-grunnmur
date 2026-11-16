/*
  motion.js: gentle motion when scrolling. Loaded on every page, in both versions.

  Cards and sections below the first screen fade in softly the first time they are
  scrolled into view. The page works the same without this script: the "reveal"
  class is only added here, so nothing is ever hidden if the script does not run.
  Visitors who have asked their device for reduced motion get no motion at all.
  (The motion at page load, the wall, rings and bars, is plain CSS in style.css.)
*/

(function () {
  if (!("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      const element = entry.target;
      observer.unobserve(element);
      element.classList.add("is-visible");
      // Afterwards remove both classes, so the element's own hover effects work as before
      setTimeout(function () { element.classList.remove("reveal", "is-visible"); }, 700);
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(".card, .about-section, .home-side").forEach(function (element) {
    // What is already on screen when the page opens stays as it is: no flicker
    if (element.getBoundingClientRect().top < window.innerHeight) return;
    element.classList.add("reveal");
    observer.observe(element);
  });
})();
