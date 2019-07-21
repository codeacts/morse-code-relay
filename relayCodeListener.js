var _messageChannels = [0, 1, 4, 7];
var message = "";
var _tempCode = "";
var alphaMorse = {};
alphaMorse["01"] = 'A';
alphaMorse["1000"] = 'B';
alphaMorse["1010"] = 'C';
alphaMorse["100"] = 'D';
alphaMorse["0"] = 'E';
alphaMorse["0010"] = 'F';
alphaMorse["110"] = 'G';
alphaMorse["0000"] = 'H';
alphaMorse["00"] = 'I';
alphaMorse["0111"] = 'J';
alphaMorse["101"] = 'K';
alphaMorse["0100"] = 'L';
alphaMorse["11"] = 'M';
alphaMorse["10"] = 'N';
alphaMorse["111"] = 'O';
alphaMorse["0110"] = 'P';
alphaMorse["1101"] = 'Q';
alphaMorse["010"] = 'R';
alphaMorse["000"] = 'S';
alphaMorse["1"] = 'T';
alphaMorse["001"] = 'U';
alphaMorse["0001"] = 'V';
alphaMorse["011"] = 'W';
alphaMorse["1001"] = 'X';
alphaMorse["1011"] = 'Y';
alphaMorse["1100"] = 'Z';
alphaMorse["1111"] = " ";


async function startProgram() {
	listenForIRMessage(_messageChannels);
}

//dot
async function onIRMessage0(channel) {
	if (channel !== 0) return;
	//await scrollMatrixText("0", {r: 0, g: 255, b: 0}, 10, true)
	setMainLed({ r: 0, g: 0, b: 0 });
	setMatrixCharacter('0', { r: 0, g: 255, b: 0 });
	_tempCode += "0";

	listenForIRMessage(_messageChannels);
}
registerEvent(EventType.onIRMessage, onIRMessage0);

//dash
async function onIRMessage1(channel) {
	if (channel !== 1) return;
	//await scrollMatrixText("1", {r: 0, g: 255, b: 0}, 10, true)
	setMainLed({ r: 0, g: 0, b: 0 });
	setMatrixCharacter('1', { r: 0, g: 255, b: 0 })
	_tempCode += "1";

	listenForIRMessage(_messageChannels);
}
registerEvent(EventType.onIRMessage, onIRMessage1);

//end-of-char
async function onIRMessage4(channel) {
	if (channel !== 4) return;
	//await scrollMatrixText(_tempCode, {r: 255, g: 0, b: 0}, 10, true);
	setMainLed({ r: 0, g: 0, b: 0 });
	setMainLed({ r: 0, g: 255, b: 0 });
	message += alphaMorse[_tempCode];
	_tempCode = "";

	listenForIRMessage(_messageChannels);

}
registerEvent(EventType.onIRMessage, onIRMessage4);

//end-of-relay
async function onIRMessage7(channel) {
	if (channel !== 7) return;
	//await scrollMatrixText("7", {r: 255, g: 0, b: 0}, 10, true)
	await scrollMatrixText(message, { r: 255, g: 0, b: 0 }, 10, true);
	await speak(message);
	setMainLed({ r: 255, g: 0, b: 0 });
	//exitProgram();

}
registerEvent(EventType.onIRMessage, onIRMessage7);
