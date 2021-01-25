// Append this script below the </html> tag in the following file: 
//  ~/.pyenv/versions/anaconda3-2019.10/envs/{CONDA_ENV}/lib/python3.7/site-packages/bokeh/core/_templates/file.html
// Currently, CONDA_ENV=terrain_env for this project, but it can be any conda environment

// <script type='text/javascript'>

  function addBlur(){
    closeNav()
    document.getElementById("responsive-grid").className = "blurred";
    document.getElementById("header").className = "blurred";
    // reset the close listener
    var close = document.getElementById("pn-closeModal");
    close.addEventListener('click', unBlur);
  }

  function unBlur(){
    openNav()
    document.getElementById("responsive-grid").className = "";
    document.getElementById("header").className = "";
    // reset the open listener
    var open = document.getElementById("sidebar").getElementsByTagName("button");
    open[0].addEventListener('click', addBlur);

  }

  function delay() {
    setTimeout(function() {
        var open = document.getElementById("sidebar").getElementsByTagName("button");
        var close = document.getElementById("pn-closeModal");
        open[0].addEventListener('click', addBlur);
        close.addEventListener('click', unBlur);
    }, 200);
  }

  if (document.readyState == 'complete') {
      delay();
  } else {
      document.onreadystatechange = function () {
          if (document.readyState === "complete") {
              delay();
          }
      }
  }

// </script>