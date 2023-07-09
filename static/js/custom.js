
  function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }

  
  document.addEventListener("scroll", function() {
    const colMd6s = document.querySelectorAll(".col-md-6");
    colMd6s.forEach((colMd6) => {
      if (isInViewport(colMd6)) {
        colMd6.classList.add("is-visible");
      }
    });
  });
  

  

  document.addEventListener("scroll", function() {
    const colMd6s = document.querySelectorAll(".col-md-6");
    colMd6s.forEach((colMd6) => {
      if (isInViewport(colMd6)) {
        colMd6.classList.add("is-visible");
        const h1 = colMd6.querySelector("h1");
        if (h1) {
          console.log(h1.innerText);
        }
      }
    });
  });
  

  let carouselContainer = document.querySelector('.carousel__container');
  let carouselItems = document.querySelectorAll('.carousel__item');
  let currentCarouselItem = 0;
  let carouselInterval = setInterval(nextCarouselItem, 1000);
  
  function nextCarouselItem() {
    currentCarouselItem = (currentCarouselItem + 1) % carouselItems.length;
    carouselContainer.style.transform = `translateX(-${currentCarouselItem * 100}%)`;
  }
  
var maxHeight = 0;
$('.col-md-4').each(function() {
  if ($(this).height() > maxHeight) {
    maxHeight = $(this).height();
  }
});
$('.col-md-4').height(maxHeight);


  
