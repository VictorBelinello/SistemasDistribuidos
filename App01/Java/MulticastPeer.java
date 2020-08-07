import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.MulticastSocket;
import java.net.SocketException;
import java.security.*;
import java.util.Scanner;

public class MulticastPeer extends Thread {
	private PublicKey pubKey;
	private PrivateKey priKey;
	private Signature sig;

	MulticastSocket s = null;
	Scanner inputScanner = null;
	InetAddress group = null;

	public int getOptionFromMenu() {
		int option = -1;
		System.out.println(" 1) Enviar mensagem ");
		System.out.println(" 2) Denunciar mensagem ");
		System.out.println(" 3) Sair ");
		option = this.inputScanner.nextInt();
		return option;
	}

	public void initSignature() throws NoSuchAlgorithmException, InvalidKeyException {
		// Inicializa objetos necessarios para assinar uma mensagem

		// Instancia usando algoritmo DSA
		sig = Signature.getInstance("DSA");

		//Gerando chaves publica e privada usando o mesmo algoritmo DSA
		KeyPairGenerator kpg = KeyPairGenerator.getInstance("DSA");
		SecureRandom rand = new SecureRandom();
		kpg.initialize(512, rand);
		KeyPair pair = kpg.genKeyPair();
		this.pubKey = pair.getPublic();
		this.priKey = pair.getPrivate();

		// Inicialização do objeto com chave privada
		sig.initSign(priKey);
	}

	public void sendSignedMessage(String msg) throws InvalidKeyException, IOException, SignatureException {
		// Envia mensagem utilizando a assinatura previamente criada
		byte[] m = msg.getBytes();
		this.sig.update(m);
		byte[] signature = this.sig.sign();
		String sigString = new String(signature, "UTF8");
		System.out.println("Minha chave publica é " + sigString );
		DatagramPacket messageOut = new DatagramPacket(sigString.getBytes(), sigString.getBytes().length, this.group, 6789);
		s.send(messageOut);
		DatagramPacket messageOutOriginal = new DatagramPacket(m, m.length, this.group, 6789);
		s.send(messageOutOriginal);
	}

	public MulticastPeer(InetAddress group) {
		int option = 0;
		try {
			// Salva o IP do grupo multicast
			this.group = group;
			// Inicializa assinatura (cria as chaves publica e privada)
			initSignature();

			// Instancia scanner para ler input do usuario
			inputScanner = new Scanner(System.in);

			// Entra no grupo multicast
			s = new MulticastSocket(6789);
			s.joinGroup(this.group);

			// Inicia thread de leitura de mensagens (metodo run)
			this.start();

			sendSignedMessage("Cheguei na parada");
			// while (option != 3) {
			// 	//option = getOptionFromMenu();
			// 	//System.out.println("Opção selecionada " + option);
			// 	//if (option == 1) {
			// 	System.out.println(" Digite a mensagem e pressione ENTER para enviar");
			// 	System.out.println(" Pressione ENTER sem digitar mensagem para fechar a aplicação");
			// 	String msg = inputScanner.nextLine();
			// 	if (msg.isEmpty()) {
			// 		break;
			// 	}

			// 	//}
			// }
			s.leaveGroup(this.group);
		} catch (NoSuchAlgorithmException | InvalidKeyException | SignatureException e) {
			System.out.println("Signature: " + e.getMessage());
		} catch (SocketException e) {
			System.out.println("Socket: " + e.getMessage());
		} catch (IOException e) {
			System.out.println("IO 2: " + e.getMessage());
		} finally {
			if (s != null) {
				s.close();
			}

			if (inputScanner != null) {
				inputScanner.close();
			}

		}
	}

	public void run() {
		try {
			byte[] buffer = new byte[1000];
			while (true) { // get messages from others in group
				DatagramPacket messageIn = new DatagramPacket(buffer, buffer.length);
				this.s.receive(messageIn);
				System.out.println("Received: " + new String(messageIn.getData(), "UTF8"));
			}
		} catch (IOException e) {
			System.out.println("IO: " + e.getMessage());
		}
	}

}
