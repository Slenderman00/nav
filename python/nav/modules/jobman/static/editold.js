
plot1 = document.getElementById('plot1')
regexRadio = document.getElementById('plot2')
plot3 = document.getElementById('plot3')

form = document.getElementById('jobform')


let plotEvent = (event) => {

    console.log("plotEvent")

    if(regexRadio.checked) {
        document.getElementById('regex').readOnly = false
    } else {
        document.getElementById('regex').readOnly = true
    }
}


let validateName = (name) => {
    console.log("validateName")
    if(name.length < 3) {
        return false
    }
    return true
}

let validateDescription = (description) => {
    console.log("validateDescription")
    if(description.length < 3) {
        return false
    }
    return true
}

let validateCommand = (command) => {
    console.log("validateCommand")
    if(command.length < 3) {
        return false
    }
    return true
}

let submitEvent = (event) => {
    console.log("submitEvent")
    event.preventDefault()

    data = new FormData(form)

    let validated = true

    if(!validateName(data.get('name'))) {
        validated = false
        console.log("name not valid")
    }
    if(!validateDescription(data.get('description'))) {
        validated = false
        console.log("description not valid")
    }
    if(!validateCommand(data.get('command'))) {
        validated = false
        console.log("command not valid")
    }


    console.log(data.get('plot'))
    if(data.get('plot') == '2') {
        console.log("regex")
        if(!validateCommand(data.get('regex'))) {
            validated = false
            console.log("regex not valid")
        }
    }

    if(validated) {
        console.log("validated")
        form.submit()
    } else {
        console.log("not validated")
        //alert
        alert("Please fill in all fields")
    }

    //if true submit form
    //form.submit()
}

plot1.onchange = plotEvent
plot3.onchange = plotEvent
regexRadio.onchange = plotEvent

form.onsubmit = submitEvent