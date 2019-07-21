var alphaMorse = {};
alphaMorse['A'] = "01";
alphaMorse['B'] = "1000";
alphaMorse['C'] = "1010";
alphaMorse['D'] = "100";
alphaMorse['E'] = "0";
alphaMorse['F'] = "0010";
alphaMorse['G'] = "110";
alphaMorse['H'] = "0000";
alphaMorse['I'] = "00";
alphaMorse['J'] = "0111";
alphaMorse['K'] = "101";
alphaMorse['L'] = "0100";
alphaMorse['M'] = "11";
alphaMorse['N'] = "10";
alphaMorse['O'] = "111";
alphaMorse['P'] = "0110";
alphaMorse['Q'] = "1101";
alphaMorse['R'] = "010";
alphaMorse['S'] = "000";
alphaMorse['T'] = "1";
alphaMorse['U'] = "001";
alphaMorse['V'] = "0001";
alphaMorse['W'] = "011";
alphaMorse['X'] = "1001";
alphaMorse['Y'] = "1011";
alphaMorse['Z'] = "1100";
alphaMorse[" "] = "1111";

var message = "This is Team Blue";
message = message.toUpperCase();

async function startProgram() {
	for (var j = 0; j < message.length; j++) {
		for (var i = 0; i < alphaMorse[message[j]].length; i++) {
			setMatrixCharacter(alphaMorse[message[j]][i], { r: 0, g: 255, b: 0 });
			await delay(1);
			setMainLed({r: 0, g: 0, b: 0});
			await delay(1);
		}
		setMainLed({r: 0, g: 255, b: 0});
		await delay(1);
	}
	setMainLed({r: 255, g: 0, b: 0});
}
