/**
 * Send POST request when <a> tag clicked.
 * Usage Example:
 *   <a href="/logout" onclick="sendPost(event)">Logout</a>
 */
function sendPost(event) {
  event.preventDefault();
  var form = document.createElement('form');
  form.action = event.target.href;
  form.method = 'post';
  document.body.appendChild(form);
  form.submit();
}
