document.addEventListener('DOMContentLoaded', function() {
    // JavaScript functionality goes here if needed.
    console.log('JavaScript loaded.');
});
  document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const workDateCheckboxes = document.querySelectorAll('input[name="work_dates"]');
    
    form.addEventListener('submit', function(event) {
      const checkedCount = Array.from(workDateCheckboxes).filter(checkbox => checkbox.checked).length;
      if (checkedCount < 3) {
        alert('You must select at least 3 work dates.');
        event.preventDefault();
      }
    });
  });

