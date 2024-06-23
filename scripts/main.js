
const START_MARKER_SIZE = 2;
const SOU_COLOR = 'rgba(45,150,50,1.0)';
const REC_COLOR = 'rgba(15,80,150,1.0)';
const PAT_COLOR = 'rgba(0,0,0,1.0)';
const SELECTED_SOURCE_COLOR = "black";
const UPDATE_ENDPOINT = 'https://sergeevsergei.ru/sps3d_api/update';
const UPLOAD_ENDPOINT = 'https://sergeevsergei.ru/sps3d_api/upload';
const TEST_DATA_ENDPOINT = 'https://sergeevsergei.ru/sps3d_api/testdata';
const REV21_REC_FORMAT = 'LINE:2:11,POINT:12:21,X:47:55,Y:56:65,Z:66:71';
const REV21_SOU_FORMAT = 'LINE:2:11,POINT:12:21,UPHOLE:39:40,DEPTH:41:46,X:47:55,Y:56:65,Z:66:71';
const REV21_REL_FORMAT = 'SLINE:18:27,SPOINT:28:37,FROMCH:39:43,TOCH:44:48,RLINE:50:59,FROMREC:60:69,TOREC:70:79';

var plotDiv = document.getElementById("survey");
const sourceSizeRange = document.getElementById("sourceSizeRange");
sourceSizeRange.setAttribute("value", START_MARKER_SIZE);
const receiverSizeRange = document.getElementById("receiverSizeRange");
receiverSizeRange.setAttribute("value", START_MARKER_SIZE);
const patternSizeRange = document.getElementById("patternSizeRange");
patternSizeRange.setAttribute("value", START_MARKER_SIZE*2);
const receiverShowCheckbox = document.getElementById("recShowTable");
const sourceShowCheckbox = document.getElementById("souShowTable");
const patternShowCheckbox = document.getElementById("relShowTable");
const receiverVisibilityCheckbox = document.getElementById("receiverVisibilityCheckbox");
const sourceVisibilityCheckbox = document.getElementById("sourceVisibilityCheckbox");
const patternVisibilityCheckbox = document.getElementById("patternVisibilityCheckbox");
const recFmtChooser = document.getElementById("recFormatChooser")
const souFmtChooser = document.getElementById("souFormatChooser")
const relFmtChooser = document.getElementById("relFormatChooser")

receiverVisibilityCheckbox.checked = true;

function resetTables() {
   if (!receiverShowCheckbox.checked) {
        receiverShowCheckbox.checked=true;
        receiverShowCheckbox.onclick();
    }
   if (!sourceShowCheckbox.checked) {
        sourceShowCheckbox.checked=true;
        sourceShowCheckbox.onclick();
   }
   if (!patternShowCheckbox.checked) {
       patternShowCheckbox.checked=true;
       patternShowCheckbox.onclick();   
   }
}

function reset_plot(sou_x_coords, sou_y_coords, rec_x_coords, rec_y_coords, pattern_x_coords, pattern_y_coords, selected_source_x, selected_source_y, title){    
    resetTables();
     
    var min_x = Math.min(...sou_x_coords, ...rec_x_coords);
    var max_x = Math.max(...sou_x_coords, ...rec_x_coords);
    var min_y = Math.min(...sou_y_coords, ...rec_y_coords);
    var max_y = Math.max(...sou_y_coords, ...rec_y_coords);

    var sou_data = {
        name : 'Source',
        x : sou_x_coords,
        y : sou_y_coords,
        mode : 'markers',
        marker: {
            size: sourceSizeRange.value,      
            color: SOU_COLOR,
        },
        type : 'scatter',
    
    };

    var rec_data = {
        name : 'Receiver', 
        x : rec_x_coords,
        y : rec_y_coords,
        mode : 'markers',
        marker: {
            size: receiverSizeRange.value,        
            color: REC_COLOR,
        },
        type : 'scatter',
    
    };

    var pat_data = {
        name : 'Pattern', 
        x : pattern_x_coords,
        y : pattern_y_coords,
        mode : 'markers',
        marker: {
            size: patternSizeRange.value,        
            color: PAT_COLOR,
        },
        type : 'scatter',
    
    };

    var selected_source_data = {
        name : 'SelSource',
        x : [parseInt(selected_source_x)],
        y : [parseInt(selected_source_y)],
        mode : 'markers',
        marker : {
            size: patternSizeRange.value*2,
            color: 'green',
        },
        type : 'scatter',      
    };

    var data = [sou_data, rec_data, pat_data, selected_source_data];
  

    var layout = {
        title: title,
        font: {size: 18},
        xaxis: {
        
            scaleratio: 1,
            tickformat: ',1f',
            tickfont: {
                size: 10  
            },
            range: [min_x, max_x],
            
        },
        yaxis: {
            scaleanchor: 'x',
            scaleratio: 1,
            tickformat: ',1f',        
            tickfont: {
                size: 10  
            },
            range: [min_y, max_y],
        },    
        hovermode:'closest',
        height: 700,
       
        showlegend : false,
    };

    var config = {
        responsive: true,
        modeBarButtonsToRemove:['select2d','lasso2d', 'zoomin2d', 'zoomout2d'],
        displayModeBar: true,
        showAxisDragHandles : false,
    };

    Plotly.newPlot(plotDiv, data, layout, config);
    const x_span = document.getElementById("selectedSourceX");
    const y_span = document.getElementById("selectedSourceY");
    x_span.innerHTML = selected_source_x;
    y_span.innerHTML = selected_source_y;

    plotDiv.on('plotly_click', function(data){
    
        if (data.points[0].curveNumber === 0) {
           setSelectedSource(data.points[0].x, data.points[0].y);
           const formData = new FormData();
           formData.append('sou_x', data.points[0].x);
           formData.append('sou_y', data.points[0].y);
           fetch(UPDATE_ENDPOINT, {method: 'POST', body: JSON.stringify([data.points[0].x, data.points[0].y]),
            headers: {'Content-Type':'application/json'} })
            .then(response => response.json())
            .then(received_data => {
                //console.log(received_data);
                setAtctivePattern(received_data.x, received_data.y);
              

            });    
        }
    });

}    

reset_plot([], [], [], [], [], [], [], [], 'Данные не загружены');


function setSelectedSource(xx, yy) {   
    
    Plotly.restyle(plotDiv, {'x': [[xx]], 'y': [[yy]]}, [3]);   
    
    const x_span = document.getElementById("selectedSourceX");
    const y_span = document.getElementById("selectedSourceY");
    x_span.innerHTML = xx;
    y_span.innerHTML = yy;
}

function setAtctivePattern(pat_x, pat_y) {
    var data_update = {        
        x : [pat_x],
        y : [pat_y],       
    }  
   // console.log('DATA UPDATE: ', data_update)
    
    Plotly.restyle(plotDiv, data_update, [2]);       
   // Plotly.restyle(plotDiv, {y: [pat_y]}, [2]);  
}



sourceSizeRange.addEventListener('input', function() {
    var update = {
        marker: {
            size: this.value,          
            color: SOU_COLOR,
          },
    }
    Plotly.restyle(plotDiv, update, 0);
});

receiverSizeRange.addEventListener('input', function() {
    var update = {
        marker: {
            size: this.value,
            color: REC_COLOR,        
          },
    }
    Plotly.restyle(plotDiv, update, 1);
});


patternSizeRange.addEventListener('input', function() {
    var update = {
        marker: {
            size: this.value,
            color: PAT_COLOR,     
          },
    }  
    Plotly.restyle(plotDiv, update, [2,3]);

});



sourceVisibilityCheckbox.addEventListener('change', function(){
    var update = {       
            visible: this.checked,
        }
    Plotly.restyle(plotDiv, update, 0)
})


receiverVisibilityCheckbox.addEventListener('change', function(){
    var update = {       
            visible: this.checked,
        }
    Plotly.restyle(plotDiv, update, 1)
})

patternVisibilityCheckbox.addEventListener('change', function(){
    var update = {       
            visible: this.checked,
    }             
  
    Plotly.restyle(plotDiv, update, [2, 3])
    
})

function replaceNumbersInString(inputString, numbersArray) {
    // Split the input string by commas to get individual key-value pairs
    const pairs = inputString.split(',');
    
    // Initialize an index to keep track of the position in the numbersArray
    let numIndex = 0;

    // Map over each pair to replace the numbers
    const result = pairs.map(pair => {
        // Split each pair by colon to separate the key and the numbers
        const parts = pair.split(':');

        // Replace the numbers in the parts with the numbers from the array
        const replacedParts = parts.map(part => {
            // Check if the part is a number (or can be converted to a number)
            if (!isNaN(part)) {
                // Replace the number with the corresponding number from the array
                const newPart = numbersArray[numIndex];
                numIndex++;
                return newPart;
            }
            // If it's not a number, return the part as is
            return part;
        });

        // Join the parts back together with colons
        return replacedParts.join(':');
    });

    // Join the result array back together with commas
    return result.join(',');
}

const submitButton = document.getElementById('filesSubmit');
submitButton.addEventListener('click', async function() {
    // Проверяем, выбраны ли файлы в file input 1 и 2
    const fileInput1 = document.getElementById('rFileUpload');
    const fileInput2 = document.getElementById('sFileUpload');
    const fileInput3 = document.getElementById('xFileUpload');

       if (!fileInput1.files.length || !fileInput2.files.length || !fileInput3.files.length) {
        alert('Выберите R-, S- и X-файл!');
        return;
    }
    
    var rFormat = "rev2.1";
    var sFormat = "rev2.1";
    var xFormat = "rev2.1";

    const recFmtChooser = document.getElementById("recFormatChooser")
    let inputElements = recFmtChooser.querySelectorAll('input');
    let inputValues = [];
    inputElements.forEach(input => {
        inputValues.push(input.value);
    });   
    if (!document.getElementById("recShowTable").checked) {
        rFormat = replaceNumbersInString(REV21_REC_FORMAT, inputValues)        
    }
    const souFmtChooser = document.getElementById("souFormatChooser")
    inputElements = souFmtChooser.querySelectorAll('input');
    inputValues = [];
    inputElements.forEach(input => {
        inputValues.push(input.value);
    });   
    if (!document.getElementById("souShowTable").checked) {
        sFormat = replaceNumbersInString(REV21_SOU_FORMAT, inputValues)        
    }
   
    inputElements = relFmtChooser.querySelectorAll('input');
    inputValues = [];
    inputElements.forEach(input => {
        inputValues.push(input.value);
    });   
    if (!document.getElementById("relShowTable").checked) {
        xFormat = replaceNumbersInString(REV21_REL_FORMAT, inputValues)        
    }
    //console.log(rFormat, sFormat, xFormat);

    const formData = new FormData();
    if (fileInput1.files) {
        formData.append('rFile', fileInput1.files[0]);
        formData.append('rFormat', rFormat);
    }   
    if (fileInput2.files) { 
        formData.append('sFile', fileInput2.files[0]);
        formData.append('sFormat', sFormat);
    }
    if (fileInput3.files) {    
        formData.append('xFile', fileInput3.files[0]);
        formData.append('xFormat', xFormat);
    }    

    try {
        const response = await fetch(UPLOAD_ENDPOINT, {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();       
        let plot_title = fileInput1.files[0].name + ", "+ fileInput2.files[0].name + ", " + fileInput3.files[0].name;
        reset_plot(data.sou_x, data.sou_y, data.rec_x, data.rec_y, data.pat_x, data.pat_y, data.sel_sou_x, data.sel_sou_y, plot_title);
      
    } catch (error) {
        console.error('Ошибка:', error);
    }
});

const testdataButton = document.getElementById('testDataLoad');
testdataButton.addEventListener('click', async function() {
    try {
        const response = await fetch(TEST_DATA_ENDPOINT, {method:'GET'});
        const data = await response.json();
        reset_plot(data.sou_x, data.sou_y, data.rec_x, data.rec_y, data.pat_x, data.pat_y, data.sel_sou_x, data.sel_sou_y, "Тестовая съемка");
       // console.log(plotDiv.data)
    } catch (error) {
        console.error('Ошибка:', error);
    }
});
