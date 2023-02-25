const instance = axios.create({withCredentials: true})
const visitsChart = new Chart(
  document.getElementById('visits'),
  {
    type: 'bar',
    data: {
      datasets: [
        {
          label: 'Number of visits'
        }
      ]
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Restaurants Visited',
          font: {
            size: 24
          }
        }
      },
      scales: {
        y: {
          ticks: {
            autoSkip: false
          }
        }
      }
    },
  }
);

const spentChart = new Chart(
  document.getElementById('spent'),
  {
    type: 'bar',
    data: {
      datasets: [
        {
          label: 'Amount Spent'
        }
      ]
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Amount Spent',
          font: {
            size: 24
          }
        }
      },
      scales: {
        y: {
          ticks: {
            autoSkip: false
          }
        }
      }
    },
  });

  const expenditureChart = new Chart(
    document.getElementById('dailyExpenditure'),
    {
      type: 'bar',
      data: {
        datasets: [
          {
            label: 'Amount Spent'
          }
        ]
      },
      options: {
        indexAxis: 'x',
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: 'Daily Expenditure',
            font: {
              size: 24
            }
          }
        }
      },
    });

$(function() {
  $('#daterange_form').on('submit', onClickUpdate);
  $('#daterange_form').submit();
});

async function onClickUpdate(e) {
  e.preventDefault();
  const startdate = $('#startdate').val();
  const enddate = $('#enddate').val();
  const url = `${window.location.protocol + "//" + window.location.host}/charts/data?startdate=${startdate}&enddate=${enddate}`;
  const response = await instance.get(url);
  
  if (response.status != 200) {
    alert("Server error");
    return;
  }

  updateVisitsChart(response.data.visits)
  updateSpentChart(response.data.spent)
  updateExpenditureChart(startdate, enddate, response.data.daily)
}

function updateVisitsChart(data) {
  // sort by most visits
  data.sort(function(x, y) {
    if (x.visits < y.visits) {
      return 1;
    } else if (x.visits > y.visits) {
      return -1;
    } else {
      return 0;
    }
  })

  visitsChart.data.labels = data.map(ele=>ele.restaurant)
  visitsChart.data.datasets[0].data = data.map(ele=>ele.visits)
  visitsChart.update()
}

function updateSpentChart(data) {
  // sort by most spent
  data.sort(function(x, y) {
    if (x.spent < y.spent) {
      return 1;
    } else if (x.spent > y.spent) {
      return -1;
    } else {
      return 0;
    }
  })
  spentChart.data.labels = data.map(ele=>ele.restaurant)
  spentChart.data.datasets[0].data = data.map(ele=>ele.spent)
  spentChart.update()
}

function updateExpenditureChart(startdate, enddate, data) {
  const start = new Date(startdate);
  const end = new Date(enddate);
  expenditureChart.data.labels = []
  expenditureChart.data.datasets[0].data = []
  for (var day = start; day <= end; day.setDate(day.getDate() + 1)) {
    const year = day.getFullYear();
    const month = String(day.getUTCMonth()+1).padStart(2, '0')
    const day2 = String(day.getUTCDate()).padStart(2, '0')
    const date = `${year}/${month}/${day2}`
    expenditureChart.data.labels.push(date)
    const amount = data[date] || 0
    expenditureChart.data.datasets[0].data.push(amount)
  }
  expenditureChart.update()
}