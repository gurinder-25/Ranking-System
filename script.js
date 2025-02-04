const validUsername = "admin";
const validPassword = "Password123";

function validateLogin(event) {
  event.preventDefault();
  const username = document.querySelector('input[type="text"]').value;
  const password = document.querySelector('input[type="password"]').value;
  const messageBox = document.getElementById('message');

  if (username === validUsername && password === validPassword) {
    messageBox.textContent = "Login successful! Redirecting...";
    messageBox.className = "message success";
    setTimeout(() => {
      window.location.href = "home.html";
    }, 1500);
  } else if (username !== validUsername) {
    messageBox.textContent = "Invalid username. Please try again.";
    messageBox.className = "message error";
  } else {
    messageBox.textContent = "Invalid password. Please try again.";
    messageBox.className = "message error";
  }
}