
if (!localStorage.getItem('counter')) {
    localStorage.setItem('counter', 0);
}

function count() {
    let counter = localStorage.getItem('counter');
    counter++;
    document.querySelector('h1').innerHTML = counter;
    localStorage.setItem('counter', counter);

    // if (counter % 10 === 0) {
    //     alert(`Count is now ${counter}`);
    // }
}

// anonymous function and document event listener to resolve
// the "Cannot set properties of null (setting 'onclick')" error
document.addEventListener('DOMContentLoaded', function() {
    // set the onclick equal to the name of a function, without ()
    // when the button is clicked on, run the count function
    // you can set a variable equal to a function
    document.querySelector('h1').innerHTML = localStorage.getItem('counter');
    document.querySelector('button').onclick = count;

    // setInterval(count, 1000);
});
