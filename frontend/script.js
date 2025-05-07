function analyze() {
  const fileInput = document.getElementById('upload');
  const file = fileInput.files[0];
  
  if (!file) {
    alert("Пожалуйста, выберите файл изображения (JPEG/PNG)");
    return;
  }

  const resultDiv = document.getElementById("result");
  const downloadLink = document.getElementById("download");
  
  // Очистка предыдущих результатов
  resultDiv.innerText = "";
  downloadLink.style.display = "none";

  // Показываем индикатор загрузки
  resultDiv.innerText = "Идёт анализ...";

  const formData = new FormData();
  formData.append("file", file);

  fetch("https://teplo.onrender.com/analyze/", {
    method: "POST",
    body: formData,
  })
  .then(async (response) => {
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Ошибка сервера");
    }
    return response.blob();
  })
  .then((blob) => {
    const url = window.URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = "teplo_analysis.pdf";
    downloadLink.style.display = "inline-block";
    resultDiv.innerText = "Анализ завершён!";
  })
  .catch((error) => {
    console.error("Ошибка:", error);
    resultDiv.innerText = "Ошибка: " + error.message;
  });
}

// Обработка drag and drop
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('upload');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  uploadArea.addEventListener(eventName, preventDefaults, false);
  document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
  uploadArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
  uploadArea.addEventListener(eventName, unhighlight, false);
});

function highlight() {
  uploadArea.classList.add('highlight');
}

function unhighlight() {
  uploadArea.classList.remove('highlight');
}

uploadArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  fileInput.files = files;
  // Триггерим событие change для предпросмотра
  const event = new Event('change');
  fileInput.dispatchEvent(event);
}
