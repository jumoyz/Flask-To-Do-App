function markDone(iconElement, taskId) {
    // Send request to mark task as done
    fetch(`/complete/${taskId}`)
        .then((response) => {
            if (response.ok) {
                iconElement.classList.remove("fa-regular", "fa-circle");
                iconElement.classList.add("fa-solid", "fa-check-circle");
            } else {
                alert("Failed to mark task as done.");
            }
        });
}

function favoriteTask(taskId) {
    fetch(`/favorite/${taskId}`)
        .then((response) => {
            if (response.ok) {
                //alert("Task marked as favorite!");
                iconElement.classList.remove("fa-regular", "fa-star");
                iconElement.classList.add("fa-solid", "fa-check-star");
            } else {
                alert("Failed to mark task as favorite.");
            }
        });
}

function deleteTask(taskId) {
    fetch(`/delete/${taskId}`)
        .then((response) => {
            if (response.ok) {
                alert("Task deleted!");
                location.reload();
            } else {
                alert("Failed to delete task.");
            }
        });
}
