// 通用函数
function showMessage(message, type = 'info') {
  const messageContainer = document.getElementById('message-container');
  if (!messageContainer) return;
  
  const messageElement = document.createElement('div');
  messageElement.className = `alert alert-${type}`;
  messageElement.textContent = message;
  
  messageContainer.appendChild(messageElement);
  
  // 3秒后自动消失
  setTimeout(() => {
    messageElement.remove();
  }, 3000);
}

// 表单提交处理
async function handleFormSubmit(event, url, method = 'POST', successCallback) {
  event.preventDefault();
  
  const form = event.target;
  const formData = new FormData(form);
  const data = {};
  
  formData.forEach((value, key) => {
    data[key] = value;
  });
  
  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '操作失败');
    }
    
    const result = await response.json();
    showMessage('操作成功', 'success');
    
    if (successCallback) {
      successCallback(result);
    }
  } catch (error) {
    showMessage(error.message, 'danger');
  }
}

// 删除确认
function confirmDelete(message = '确定要删除吗？') {
  return confirm(message);
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  // 初始化消息容器
  if (!document.getElementById('message-container')) {
    const container = document.createElement('div');
    container.id = 'message-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1000';
    document.body.appendChild(container);
  }
  
  // 初始化表单提交事件
  document.querySelectorAll('form[data-submit-ajax]').forEach(form => {
    const url = form.getAttribute('action');
    const method = form.getAttribute('method') || 'POST';
    
    form.addEventListener('submit', event => {
      handleFormSubmit(event, url, method, () => {
        // 默认成功回调：刷新页面
        window.location.reload();
      });
    });
  });
});