const Modal = {
    toggleZoom() {
      document.querySelector(".modal-overlay").classList.toggle("active");
    },
    toggleHelp() {
      document.querySelector(".modal-overlay-help").classList.toggle("active");
    },
    toggleDownload() {
      document.querySelector(".tooltip").classList.toggle("active");
    },
  };