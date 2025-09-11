document.addEventListener('DOMContentLoaded', function() {
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Add form submit event listener
  document.querySelector('#compose-form').addEventListener('submit', send_mail);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Get emails from API
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Loop through each email
    emails.forEach(email => {
      // Create div for each email
      const emailDiv = document.createElement('div');
      emailDiv.style.cssText = `
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #ddd;
        cursor: pointer;
        background-color: ${email.read ? '#f8f9fa' : 'white'};
      `;
      
      emailDiv.innerHTML = `
        <strong>From:</strong> ${email.sender}<br>
        <strong>Subject:</strong> ${email.subject}<br>
        <strong>Time:</strong> ${email.timestamp}
      `;

      // Add click event to view email
      emailDiv.addEventListener('click', () => view_email(email.id));
      
      // Add to emails view
      document.querySelector('#emails-view').appendChild(emailDiv);
    });
  })
  .catch(error => {
    console.error('Error loading emails:', error);
  });
}

function view_email(email_id) {
  // Show email view and hide others
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  // Get the email details
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Mark email as read
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({ read: true })
    });

    // Create email view content
    let emailContent = `
      <button onclick="load_mailbox('inbox')" class="btn btn-primary">← Back to Inbox</button>
    `;

    // Add Archive button (only for inbox and archive emails, not sent)
    const currentUser = document.querySelector('h2').textContent.trim();
    if (email.sender !== currentUser) {
      emailContent += `
        <button onclick="archive_email(${email_id}, ${email.archived})" class="btn btn-secondary" style="margin-left: 10px;">
          ${email.archived ? 'Unarchive' : 'Archive'}
        </button>
      `;
    }

    // Add Reply button
    emailContent += `
      <button onclick="reply_email(${email_id})" class="btn btn-success" style="margin-left: 10px;">
        Reply
      </button>
      <hr>
      
      <div style="background: #f8f9fa; padding: 15px; margin: 10px 0;">
        <strong>From:</strong> ${email.sender}<br>
        <strong>To:</strong> ${email.recipients.join(', ')}<br>
        <strong>Subject:</strong> ${email.subject}<br>
        <strong>Timestamp:</strong> ${email.timestamp}
      </div>
      
      <div style="padding: 15px; background: white; border: 1px solid #ddd;">
        ${email.body.replace(/\n/g, '<br>')}
      </div>
    `;

    document.querySelector('#email-view').innerHTML = emailContent;
  })
  .catch(error => {
    console.error('Error loading email:', error);
  });
}

function send_mail(event) {
  event.preventDefault();
  
  // Get form values
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Send email via API
  fetch('/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.error) {
      alert('Error: ' + result.error);
    } else {
      console.log('Email sent successfully');
      load_mailbox('sent');
    }
  })
  .catch(error => {
    console.error('Error sending email:', error);
    alert('Failed to send email');
  });
}

function archive_email(email_id, current_archived_status) {
  // Toggle archive status
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: !current_archived_status
    })
  })
  .then(response => {
    if (response.ok) {
      // Go back to inbox after archiving/unarchiving
      load_mailbox('inbox');
    }
  })
  .catch(error => {
    console.error('Error archiving email:', error);
  });
}

function reply_email(email_id) {
  // Get the original email
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Switch to compose view
    compose_email();
    
    // Fill in the recipient (original sender)
    document.querySelector('#compose-recipients').value = email.sender;
    
    // Fill in subject with "Re: " prefix
    let subject = email.subject;
    if (!subject.startsWith('Re: ')) {
      subject = 'Re: ' + subject;
    }
    document.querySelector('#compose-subject').value = subject;
    
    // Fill in body with original email quoted
    const replyBody = `\n\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
    document.querySelector('#compose-body').value = replyBody;
    
    // Put cursor at beginning of textarea
    document.querySelector('#compose-body').focus();
    document.querySelector('#compose-body').setSelectionRange(0, 0);
  })
  .catch(error => {
    console.error('Error loading email for reply:', error);
  });
}