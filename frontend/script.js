document.addEventListener('DOMContentLoaded', () => {
  const uploadArea = document.getElementById('upload-area');
  const fileInput = document.getElementById('upload');
  const preview = document.getElementById('preview');
  const analyzeBtn = document.getElementById('analyze-btn');
  const btnText = document.getElementById('btn-text');
  const spinner = document.getElementById('spinner');
  const resultDiv = document.getElementById('result');
  const downloadLink = document.getElementById('download');

  // Обработка выбора файла
  fileInput.addEventListener('change', handleFileSelect);

  // Обработка клика по области загрузки
  uploadArea.addEventListener('click', () => fileInput.click());

  // Drag and drop
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, highlight, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, unhighlight, false);
  });

  uploadArea.addEventListener('drop', handleDrop, false);

  // Анализ изображения
  analyzeBtn.addEventListener('click', analyze);

  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    displayPreview(file);
    analyzeBtn.disabled = false;
    resultDiv.textContent = '';
    downloadLink.style.display = 'none';
  }

  function displayPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight() {
    uploadArea.classList.add('highlight');
  }

  function unhighlight() {
    uploadArea.classList.remove('highlight');
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
      fileInput.files = files;
      const event = new Event('change');
      fileInput.dispatchEvent(event);
    }
  }

  async function analyze() {
    const file = fileInput.files[0];
    if (!file) return;

    // Подготовка UI
    analyzeBtn.disabled = true;
    btnText.textContent = 'Идёт анализ...';
    spinner.style.display = 'block';
    resultDiv.textContent = '';
    resultDiv.className = 'result-message';
    downloadLink.style.display = 'none';

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('https://teplo.onrender.com/analyze/', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка сервера');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      downloadLink.href = url;
      downloadLink.download = 'teplo_analysis.pdf';
      downloadLink.style.display = 'flex';
      
      resultDiv.textContent = 'Анализ успешно завершён!';
      resultDiv.classList.add('success');
    } catch (error) {
      console.error('Ошибка:', error);
      resultDiv.textContent = `Ошибка: ${error.message || 'Неизвестная ошибка'}`;
      resultDiv.classList.add('error');
    } finally {
      btnText.textContent = 'Анализировать';
      spinner.style.display = 'none';
      analyzeBtn.disabled = false;
    }
  }
});
