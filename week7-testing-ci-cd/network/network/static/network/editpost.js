document.addEventListener('DOMContentLoaded', function() {

    // use buttons to open edit_post
    document.querySelectorAll(".edit-post-button").forEach(button =>
        button.addEventListener("click", edit_post)
        );

    // add event listeners to likeheart
    document.querySelectorAll(".heartlike").forEach(heart =>
        heart.addEventListener("click", like_post)
        );

    // add an event listener to the form submit (edit post)
    document.querySelector('.submit-edited-post-button').addEventListener('click', submit_edited_post);

});

function edit_post(e) {
    // DEBUG
    // alert("clicked!");
    // get parent element
    let parent = e.target.parentNode;
    // get the post body within that parent
    let body = parent.querySelector('.post-body');
    // save old post body so exit isn't starting from scratch
    let old_body = body.textContent;
    // set old post body
    body.innerHTML = `<textarea>${old_body}</textarea>`;
    // unhide post_button
    let post_button = parent.querySelector('.submit-edited-post-button');
    post_button.style.display = 'inline';
}


function submit_edited_post(e) {
    // get parent element (DIV)
    let parent = e.target.parentNode;
    // get the post body within that parent
    let body = parent.querySelector('.post-body');
    // get text area within that body
    let text_area = body.querySelector('textarea');
    // save new_body
    const new_body = text_area.value;
    // save post_id
    const post_id = parent.dataset.postId;
    // const post_id = parent.querySelector('.post-id').innerHTML;

    // fetch
    fetch('/editpost', {
        method: 'POST',
        body: JSON.stringify({
            post_id: post_id,
            new_body: new_body
        })
    })
    .then(response => response.json())
    .then(result => {
    // Print result
    console.log(result);
    });

    // return body formatting
    let og_body = parent.querySelector('.post-body');
    og_body.innerHTML = `<p>${new_body}</p>`;

    // hide post_button
    let post_button = parent.querySelector('.submit-edited-post-button');
    post_button.style.display = 'none';
}


function like_post(e) {
    // get parent element (DIV)
    let parent = e.target.parentNode;
    // save author
    const author = parent.dataset.author;
    // save post_id
    const post_id = parent.dataset.postId;
    console.log(post_id)
    console.log(author)

    // fetch
    fetch('/likepost', {
        method: 'POST',
        body: JSON.stringify({
            post_id: post_id,
            author: author
        })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
  });

  let heart = parent.querySelector('.heartlike');
  const like_count = parent.querySelector('.post-likes-value');

  if (heart.getAttribute('fill') == 'black') {
    heart.setAttribute('fill', 'red');
    like_count.innerHTML = `${parseInt(like_count.textContent) + 1}`;

  } else {
    heart.setAttribute('fill', 'black');
    like_count.innerHTML = `${parseInt(like_count.textContent) - 1}`;
  }
}