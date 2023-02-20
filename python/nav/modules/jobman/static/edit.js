type = document.getElementById('id_plottype')
regex = document.getElementById('id_regex')
regex.readOnly = true

type.onchange = function() {
    if(type.value == '2') {
        regex.readOnly = false
    } else {
        regex.readOnly = true
    }
}