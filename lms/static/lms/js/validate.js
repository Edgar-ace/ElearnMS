// Shared by all the form pages.
// form = the form being submitted, name = what we are saving (e.g. "Student")
function validateForm(form, name) {
    var fields = form.querySelectorAll("input, select");

    for (var i = 0; i < fields.length; i++) {
        if (fields[i].value === "") {
            alert("Please fill in the field: " + fields[i].name);
            fields[i].focus();
            return false;   // false stops the form from submitting
        }
    }

    alert(name + " saved successfully!");
    return true;            // true lets the form submit
}