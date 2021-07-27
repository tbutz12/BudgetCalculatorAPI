var purchaseList = new Array();
var catList = new Array();

function checkBudgetAmount(cat_id, bAmount){
	if(purchaseList.length === 0){
		return 0;
	}
	var filterList = purchaseList.filter(val=>val.category_id === cat_id);
	var pAmount = filterList.reduce((acc, val)=>acc+val.amount, 0);
	if(pAmount > bAmount){
		return "overspent";
	}
	return (bAmount - pAmount).toFixed(2);
}
function setup() {
	document.getElementById("categoryButton").addEventListener("click", sendCategory, true);
	document.getElementById("purchaseButton").addEventListener("click", sendPurchase, true);
	refreshCategories();
	refreshPurchases();
}
function makeRec(method, target, retCode, handlerAction, data) {
	var httpRequest = new XMLHttpRequest();
	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = makeHandler(httpRequest, retCode, handlerAction);
	httpRequest.open(method, target);
	
	if (data) {
		httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		httpRequest.send(data);
	}
	else {
		httpRequest.send();
	}	
}
function makeHandler(httpRequest, retCode, action) {
	console.log("making handler!");
	function handler() {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
			if (httpRequest.status === retCode) {
				console.log("recieved response text:  " + httpRequest.responseText);
				action(httpRequest.responseText);
			} else {
				alert("There was a problem with the request.  you'll need to refresh the page!");
			}
		}
	}
	return handler;
}
//CLIENT SIDE LOGIC
function refreshCategories() {
	makeRec("GET", "/cats", 200, updateCategories);
}
function refreshPurchases(){
    makeRec("GET", "/purchases",200,updatePurchases)
}
function sendCategory() {
    var catName = document.getElementById("newCat").value;
    var budgetAmount = document.getElementById("catAmount").value;
	var data;
	data = "CategoryName=" + catName + "&budgetedAmount=" +budgetAmount;
	makeRec("POST", "/cats", 201, refreshCategories, data);
}
function sendPurchase() {
    var purchaseName = document.getElementById("newPurchase").value;
    var purCategory = document.getElementById("purchaseCat").value;
    var purAmount = document.getElementById("purchaseAmount").value;
	var pdate = document.getElementById("purchaseDate").value;
	var data;
	data = "Name=" + purchaseName + "&CategoryName=" +purCategory + "&Amount="+purAmount+"&Date="+pdate;
	makeRec("POST", "/purchases", 201, refreshPurchases, data);
}
function deleteCat(catID) {
	makeRec("DELETE", "/cats/" + catID, 204, refreshCategories);
}
// helper function for repop:
function addCell(row, text) {
	var newCell = row.insertCell();
	var newText = document.createTextNode(text);
	newCell.appendChild(newText);
}
//translate SQLAlchemy nonsense to Javascript object
function responseToObject(s){
	//trim leading and trailing white spaces
	s = s.trim();
	//remove double quotes from first and last position
	s = s.substring(1, s.length-1);
	//remove backslashes from JSON
	s = s.replace(/\\"+/g, '"');
	//parse JSON
	return JSON.parse(s);
}
function updateCategories(responseText) {
	console.log("repopulating categories!");
	catList = responseToObject(responseText);
	buildCategoryTable();
}
function buildCategoryTable(){
	var tab = document.getElementById("theTable");
	var tab2 = document.getElementById("uncategorized");
	var newRow, newCell, newButton;
	while (tab.rows.length > 0) {
		tab.deleteRow(0);
	}
	while (tab2.rows.length > 0){
		tab2.deleteRow(0);
	}
	for(y in purchaseList){
		var p = purchaseList[y];
		if (p.categoryName === "uncategorized"){
			newRow = tab2.insertRow();
			addCell(newRow, "Name: ");
			addCell(newRow, p.name);
			newRow = tab2.insertRow();
			addCell(newRow, "Purchase Amount: ");
			addCell(newRow, p.amount);
			newRow = tab2.insertRow();
			addCell(newRow, "Purchase Date: ");
			addCell(newRow, p.purchaseDate);
			newRow = tab2.insertRow();
		}
	}
	for(x in catList){
		var cat = catList[x];
		newRow = tab.insertRow();
		addCell(newRow, "ID: ");
		addCell(newRow, cat.id);
		newRow = tab.insertRow();
		addCell(newRow, "Category: ");
		addCell(newRow, cat.categoryName);
		newRow = tab.insertRow();
		addCell(newRow, "Budget Amount: ");
		addCell(newRow, cat.amount.toFixed(2));
		newRow = tab.insertRow();
		addCell(newRow, "Status: ");
		statusAmount = checkBudgetAmount(cat.id, cat.amount);
		addCell(newRow, statusAmount);
		newRow = tab.insertRow();
		newCell = newRow.insertCell();
		newButton = document.createElement("input");
		newButton.type = "button";
		newButton.value = "Delete " + cat.categoryName;
		newButton.addEventListener("click", function() { deleteCat(cat.categoryName); });
		newCell.appendChild(newButton);
	}
}
function updatePurchases(responseText) {
	console.log("repopulating purchase List!");
	purchaseList = responseToObject(responseText);
	buildCategoryTable();
}
// setup load event
window.addEventListener("load", setup, true);
