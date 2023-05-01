document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Add event listener to form submit (send_email)
  document.querySelector("#compose-form").addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function send_email(event) {
  event.preventDefault();

  // Select values...
  const form_recipients = document.querySelector('#compose-recipients').value;
  const form_subject = document.querySelector('#compose-subject').value;
  const form_body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: form_recipients,
      subject: form_subject,
      body: form_body
    })
  })
  .then(response => response.json())
  .then(result => {
    // Print result
    console.log(result);
    load_mailbox('sent');
  });
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Render emails
    emails.forEach((email) => {
      // DEBUG
      // console.log(email);

      // Create div
      const div = document.createElement('div');
      // Add data to div
      div.innerHTML = `Sender: ${email['sender']} <br> Subject: ${email['subject']} <br> Timestamp: ${email['timestamp']}`;
      // Style div
      div.style.border = '2px solid';
      div.style.borderRadius = '12px';
      div.style.padding = '10px 10px 10px 10px';
      div.style.marginBottom = '5 px';
      // If read, style white
      if (email['read'] === true) {
        div.style.backgroundColor = 'gray';
      } else { // Else, style gray
        div.style.backgroundColor = 'white';
      }
      // Add event listener for clicks, load_mail
      div.addEventListener('click', function() {
        // Get request for email ID
        fetch(`/emails/${email['id']}`)
          .then(response => response.json())
          .then(em => {
            // Debug
            // console.log(`Sender: ${em['sender']} ID: ${em['id']}`);

            // View email with load_mail function
            load_mail(em);
          });
        // DEBUG
        // alert('This element has been clicked!')
      });
      // Append email to #emails-view
      document.querySelector('#emails-view').append(div);
    });
  });
}

function load_mail(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Clear previous content
  document.querySelector('#email-view').innerHTML = "";
  // Create div
  const div = document.createElement('div');
  // Add data to div
  div.innerHTML = `Sender: ${email['sender']} <br>
                   Recipients: ${email['recipients']} <br>
                   Subject: ${email['subject']} <br>
                   Timestamp: ${email['timestamp']} <br>
                   Body: ${email['body']}`;
  // Style div
  div.style.border = '2px solid';
  div.style.borderRadius = '12px';
  div.style.padding = '10px 10px 10px 10px';
  div.style.margin = '10px';

  // Append email to #emails-view
  document.querySelector('#email-view').append(div);

  // Add Archive Button
  const archive_button = document.createElement('button');
  // Archive/Unarchive Functionality
  if (email['archived'] === false) {
    // Set inner HTML
    archive_button.innerHTML = 'Archive';
    // Make PUT request
    archive_button.addEventListener('click', () => {
      fetch(`/emails/${email['id']}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: true
        })
      });
      // Load Inbox
      load_mailbox('inbox');})
  } else {
    // Set inner HTML
    archive_button.innerHTML = 'Unarchive';
    // Make PUT request
    archive_button.addEventListener('click', () => {
      fetch(`/emails/${email['id']}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: false
        })
      });
      // Load Inbox
      load_mailbox('inbox');})
  }
  // Style archive_button
  archive_button.style.padding = '10px 10px 10px 10px';
  archive_button.style.margin = '5px';
  // Append archive_button to #emails-view
  document.querySelector('#email-view').append(archive_button);

  // Add Reply Button
  const reply_button = document.createElement('button');
  reply_button.innerHTML = 'Reply';
  // Call compose_email
  reply_button.addEventListener('click', () => {
    // Compose email
    compose_email();
    // Populate Fields for Reply
    // Sender
    document.querySelector('#compose-recipients').value = `${email['sender']}`;
    // Subject
    // Check for double 'Re: '
    if (email['subject'].slice(0, 4) === 'Re: ') {
      document.querySelector('#compose-subject').value = `${email['subject']}`;
    } else {
      document.querySelector('#compose-subject').value = `Re: ${email['subject']}`;
    }
    // Body
    document.querySelector('#compose-body').value = `On ${email['timestamp']} ${email['sender']} wrote:\n${email['body']}\n\n`;
    return false;
    load_mailbox('sent');
  });
  // Style reply_button
  reply_button.style.padding = '10px 10px 10px 10px';
  reply_button.style.margin = '5px';
  // Append reply_button to #emails-view
  document.querySelector('#email-view').append(reply_button);

  // Mark email as read
  fetch(`/emails/${email['id']}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
}