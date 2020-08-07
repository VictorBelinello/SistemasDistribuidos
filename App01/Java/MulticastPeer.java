import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.MulticastSocket;
import java.net.SocketException;
import java.security.InvalidKeyException;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.Signature;
import java.security.SignatureException;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class MulticastPeer extends Thread {
	private PublicKey pubKey; // Chave pública do nó 
	private PrivateKey priKey; // Chave privada do nó (usada para inicializar a assinatura)
	private Signature sig; // Assinatura própia do nó 
	private UUID id; // Identificador unico do nó

	MulticastSocket s = null; // Socket para conexão Multicast com grupo
	InetAddress group = null; //IP Multicast do grupo
	Map<UUID, Integer> nodesRep = null; //Lista das reputações dos nós no grupo
	Map<UUID, PublicKey> nodesPubKeys = null; //Lista das chaves publicas dos nós no grupo

	public void initSignature() throws NoSuchAlgorithmException, InvalidKeyException {
		// Inicializa objetos necessarios para assinar uma mensagem

		// Instancia usando algoritmo DSA
		sig = Signature.getInstance("NONEwithRSA");

		//Gerando chaves publica e privada usando o mesmo algoritmo DSA
		KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
		SecureRandom rand = new SecureRandom();
		kpg.initialize(512, rand);
		KeyPair pair = kpg.genKeyPair();
		this.pubKey = pair.getPublic();
		this.priKey = pair.getPrivate();

		// Inicialização do objeto com chave privada
		sig.initSign(priKey);
	}

	public byte[] generateSignature(String msg) throws InvalidKeyException, IOException, SignatureException {
		// Gera assinatura para mensagem passada
		byte[] m = msg.getBytes();

		this.sig.update(m);
		byte[] signature = sig.sign();

		return signature;
	}

	public void joinMulticastGroup() throws InvalidKeyException, IOException, SignatureException {
		// Entra no grupo
		s = new MulticastSocket(6789);
		s.joinGroup(this.group);

		// Precede a mensagem com o id do usuario para ser identificado e salvo pelos outros membros do grupo
		String id = this.id.toString();
		
		// Converte chave pública e UUID para byte[]
		byte[] key = this.pubKey.getEncoded();
		byte[] idBytes = id.getBytes();

		// Concatena os dois byte[]
		byte[] m = new byte[key.length + idBytes.length];
		System.arraycopy(idBytes, 0, m, 0, idBytes.length);
		System.arraycopy(key, 0, m, idBytes.length, key.length);

		// Envia mensagem
		DatagramPacket messageOut = new DatagramPacket(m, m.length, group, 6789);
		s.send(messageOut);
	}

	public boolean isFirstTime(UUID id) {
		// Se nó não estiver nas listas adiciona, efetivamente só uma comparação precisa ser feita.
		if (!this.nodesPubKeys.containsKey(id) && !this.nodesRep.containsKey(id)) {
			return true;
		}
		return false;
	}

	public void addNode(UUID id, PublicKey key){
		this.nodesPubKeys.put(id, key);	
		this.nodesRep.put(id, 100);	// Inicia com reputação 100
	}

	public PublicKey extractKey(byte[] encodedKey) throws NoSuchAlgorithmException, InvalidKeySpecException{
		
		KeyFactory kf = KeyFactory.getInstance("RSA");

		X509EncodedKeySpec encodedKeySpec = new X509EncodedKeySpec(encodedKey);
		
		return kf.generatePublic(encodedKeySpec);
	}

	public boolean 

	public MulticastPeer(InetAddress group) {
		boolean continueChat = true;
		try {
			// Salva o IP do grupo multicast
			this.group = group;

			// Inicializa assinatura (cria as chaves publica e privada)
			initSignature();

			this.nodesRep = new HashMap<UUID, Integer>();
			this.nodesPubKeys = new HashMap<UUID, PublicKey>();

			// Obtem um identificador unico
			this.id = UUID.randomUUID();

			System.out.println("Your ID is: " + this.id);

			// Entra no grupo multicast
			joinMulticastGroup();

			// Inicia thread de leitura de mensagens (metodo run)
			this.start();

			while(continueChat){
				
			}

			s.leaveGroup(this.group);
		} catch (NoSuchAlgorithmException | InvalidKeyException | SignatureException e) {
			System.out.println("Signature: " + e.getMessage());
		} catch (SocketException e) {
			System.out.println("Socket: " + e.getMessage());
		} catch (IOException e) {
			System.out.println("IO 2: " + e.getMessage());
		}
	}

	public void run() {
		try {
			byte[] buffer = new byte[1000];
			while (true) { // get messages from others in group
				DatagramPacket messageIn = new DatagramPacket(buffer, buffer.length);
				//this.sig.initVerify(certificate);
				//this.sig.update(buffer.getBytes());
				//if (this.sig.verify(signature))
				this.s.receive(messageIn);
				String message = new String(messageIn.getData(), "UTF8"); // UUID tem 32bytes + 4 caracters para os separadores (-)
				UUID senderID = UUID.fromString(message.substring(0, 36));

				// Verifica se é a primeira vez que o nó manda uma mensagem
				if(isFirstTime(senderID)){
					// Se for a mensagem é a chave publica do remetente
					// Adiciona nó nas listas
					byte[] encodedKey = Arrays.copyOfRange(messageIn.getData(), 36, messageIn.getData().length);
					PublicKey pubKey = extractKey(encodedKey);
					addNode(senderID, pubKey);
					System.out.print(senderID.toString() + ": *Public Key*");
					continue;
				}
				//System.out.print(senderID.toString() + ": ");
				//System.out.println(pubKey);
				//System.out.printf("[%s]: %s\n", senderID.toString(), message.substring(36));
			}
		} catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
			System.out.println("Public Key: " + e.getMessage());
		} catch (IOException e) {
			System.out.println("IO: " + e.getMessage());
		}
	}

}
