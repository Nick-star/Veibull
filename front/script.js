const openModal = (triggerSelector, modalDataSelector) => { 
    const trigger = document.querySelector(triggerSelector)
    const modal = document.querySelector(modalDataSelector)
    if (!trigger || !modal) return
    trigger.addEventListener('click', e => { 
      e.preventDefault() 
      modal.classList.add('modal_active') 
    })
  }
  openModal('.dates', '.modal[data-modal="one"]') // Запускаем функцию и передаем селекторы для второго модального окна
  
  const closeModal = () => { 
    const modals = document.querySelectorAll('.modal') 
    if (!modals) return
    modals.forEach(el => {
      el.addEventListener('click', e => {
        if (e.target.closest('.modal__close')) { 
          el.classList.remove('modal_active') 
        }
        if (!e.target.closest('.modal__body')) { 
          el.classList.remove('modal_active')
        }
      })
    })
  }
  closeModal()
  

let ctx = document.querySelector('#myChart'). getContext('2d');
let myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [1,2,3,4,5],
        datasets: [{
            label: 'Students',
            data: [50, 40, 25, 30, 15],
            backgroundColor: ['white'],
            borderColor: ['red', 'yellow', 'green', 'blue', 'purple'],
            borderWidth: 4
        }]
    },
    options: {}
})
