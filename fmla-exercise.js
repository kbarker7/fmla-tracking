const checkTimeForm = document.getElementById("fmla-check-time-form");
const checkTimeButton = document.getElementById("check-time-submit");
const requestTimeForm = document.getElementById("fmla-request-time-form");
const requestTimeButton = document.getElementById("request-time-submit");

checkTimeButton.addEventListener("click", (e) => {
    e.preventDefault();
    const employeeId = checkTimeForm.employeeId.value;
    const requestYear = checkTimeForm.requestYear.value;
    var params = "?id=" + employeeId + "&year=" + requestYear;

    fetch("https://dhxpszbct2.execute-api.us-east-1.amazonaws.com/dev/fmla" + params)
    .then(response => response.json())
    .then(data => {
        document.getElementById("resultHeader").innerHTML = "Results for Requested Time Check";
        document.getElementById("employeeIdResult").innerHTML = "Id: " + data.employeeId;
        document.getElementById("requestedYearResult").innerHTML = "Yr: " + data.year;
        document.getElementById("hoursUsedResult").innerHTML = "Hours Used: " + data.hoursUsed;
        document.getElementById("hoursAvailableResult").innerHTML = "Hours Available: " + data.hoursAvailable;
    })
    .catch(error => console.log("error", error)); 

})

requestTimeButton.addEventListener("click", (e) => {
    e.preventDefault();
    const employeeId = requestTimeForm.employeeId.value;
    const startDate = requestTimeForm.startDate.value;
    const endDate = requestTimeForm.endDate.value;

    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    var raw = JSON.stringify({"employeeId":employeeId,"startDate":startDate,"endDate":endDate});
    var requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: raw,
        redirect: "follow"
    };

    fetch("https://dhxpszbct2.execute-api.us-east-1.amazonaws.com/dev/fmla", requestOptions)
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log(data.body)
        jsonValue = JSON.parse(data.body)
        console.log(jsonValue.employeeId)
        console.log(jsonValue.message)
        document.getElementById("resultHeader").innerHTML = "Results for Submitted Time Check";
        document.getElementById("employeeIdResult").innerHTML = "Employee Id: \t" +  jsonValue.employeeId;
        document.getElementById("requestedYearResult").innerHTML = "Requested Year: \t" + jsonValue.message;
        document.getElementById("hoursUsedResult").innerHTML = "Hours Requested: \t" + jsonValue.requestedHours;
        document.getElementById("hoursAvailableResult").innerHTML = "Hours Accepted: \t" + jsonValue.acceptedHours;
    })
    .catch(error => console.log("error", error)); 
})

function switchTabs(evt, tabName) {
  var i, tabcontent, tablinks;

  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}