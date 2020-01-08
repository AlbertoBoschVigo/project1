var counter = 1;
var paginaActual = 1;
var maxPagina = -2;
var finTr = paginaActual * 10;
var inicioTr = finTr - 10;

document.addEventListener('DOMContentLoaded', function (){
    selectorVisibilidad();
    /*var papa = document.querySelector('tbody');
    var hijos = papa.children;
    for (i=0; i<hijos.length; i++){
        if(i+1 > inicioTr && i+1 <= finTr){
            hijos[i].style.display = 'block';
            //hijos[i].style.visibility = 'visible';
        }
        else{
            hijos[i].style.display = 'none';
            //hijos[i].style.visibility = 'hidden';
        }
    }*/
    document.querySelectorAll('.page-item').forEach(function(elemento) {
        maxPagina ++;
    });
    /*
    document.querySelectorAll('.escondible').forEach(function(item) {
        if(counter > inicioTr && counter <= finTr){
            item.style.display = 'block';
        }
        else{
            item.style.display = 'none';
        }
        counter ++;
    });
    */      
});

function funcPaginar(objetctA) {
    var aux = objetctA.innerHTML;
    if (aux == "Previous"){
        if (paginaActual > 1){
            paginaActual --;
        }
    }
    else if (aux == "Next"){
        if (paginaActual< maxPagina){
            paginaActual ++;
        }
        
    }
    else{
        paginaActual = aux;
    }
    counter = 1;
    document.querySelectorAll('.page-item').forEach(function(elemento) {
        var hijo = elemento.children[0].innerHTML;
        elemento.classList.remove("active");
        if (hijo == paginaActual){
            finTr = paginaActual * 10;
            inicioTr = finTr - 10;
            elemento.classList.add("active");
            selectorVisibilidad();
        }
    });
};

function selectorVisibilidad(){
    var papa = document.querySelector('tbody');
    var hijos = papa.children;
    var nietos;
    for (i=0; i<hijos.length; i++){
        if(i+1 > inicioTr && i+1 <= finTr){
            hijos[i].style.display = 'block';
            /*nietos = hijos[i].children;
            for (j=0; j<hijos.length; j++){
                nietos[j].style.display = 'block';
            }
            //hijos[i].dataset.visible = 'true';*/
        }
        else{
            hijos[i].style.display = 'none';
            /*nietos = hijos[i].children;
            for (j=0; j<hijos.length; j++){
                nietos[j].style.display = 'block';
            }
            //hijos[i].dataset.visible = 'false';*/
        }
    }
};