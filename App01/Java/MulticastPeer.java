import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.MulticastSocket;
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
	private UUID uuid; // Identificador unico do nó
	private MulticastSocket s = null; // Socket para conexão Multicast com grupo
	private InetAddress group = null; // IP Multicast do grupo
	private Map<UUID, Integer> nodesRep = null; // Lista das reputações dos nós no grupo
	private Map<UUID, PublicKey> nodesPubKeys = null; // Lista das chaves publicas dos nós no grupo
	private final String ALGORITHM = "DSA"; // Usa algoritmo DSA para gerar chaves/assinatura

	final char TOM_PublicKey = '0'; // Mensagem enviando a chave publica
	final char TOM_Alert = '1'; // Mensagem enviando um alerta sobre outra mensagem (fake news)
	final char TOM_Normal = '2'; // Mensagem comum

	final int HEADER_SIZE = 41; // Header com tamanho fixo de 41bytes

	public MulticastPeer() {
		this.nodesPubKeys = new HashMap<UUID, PublicKey>();
		this.nodesRep = new HashMap<UUID, Integer>();
	}

	public void initSignature() throws NoSuchAlgorithmException, InvalidKeyException {
		// Inicializa objetos necessarios para assinar uma mensagem

		// Instancia usando algoritmo definido
		sig = Signature.getInstance(ALGORITHM);

		// Gerando chaves publica e privada usando o mesmo algoritmo
		KeyPairGenerator kpg = KeyPairGenerator.getInstance(ALGORITHM);
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
		Header header = new Header(this.uuid, TOM_PublicKey, 97);

		// Converte chave pública para byte[]
		byte[] key = this.pubKey.getEncoded();

		// Combina header e mensagem(key)
		byte[] m = header.appendHeaderTo(key);

		// Envia mensagem
		DatagramPacket messageOut = new DatagramPacket(m, m.length, group, 6789);
		s.send(messageOut);
	}

	public void addNode(UUID id, PublicKey key) {
		this.nodesPubKeys.put(id, key);
		this.nodesRep.put(id, 100); // Inicia com reputação 100
	}

	public PublicKey extractKey(byte[] encodedKey) throws NoSuchAlgorithmException, InvalidKeySpecException {

		KeyFactory kf = KeyFactory.getInstance(ALGORITHM);

		X509EncodedKeySpec encodedKeySpec = new X509EncodedKeySpec(encodedKey);

		return kf.generatePublic(encodedKeySpec);
	}

	public void run() {
		try {
			byte[] buffer = new byte[1000];
			while (true) { // get messages from others in group
				DatagramPacket messageIn = new DatagramPacket(buffer, buffer.length);
				this.s.receive(messageIn);
				byte[] raw = messageIn.getData();

				Header header = Header.extractHeader(raw);

				UUID uuid = header.uuid;

				// Verifica se não está na lista, ou seja, é um novo nó
				if (!this.nodesPubKeys.containsKey(uuid) && !this.nodesRep.containsKey(uuid)) {
					// Se for, a mensagem é a chave publica do remetente

					// Extrai a chave pública 
					byte[] encodedKey = Arrays.copyOfRange(messageIn.getData(), HEADER_SIZE,
							messageIn.getData().length);
					PublicKey pubKey = extractKey(encodedKey);

					// Adiciona nó nas listas
					addNode(uuid, pubKey);

					// Como pubKey apenas mostra *<Algoritmo> Public Key* para não poluir o chat
					System.out.printf("[%s]: %s Public Key\n", uuid.toString(), pubKey.getAlgorithm());
					System.exit(0);
				} else {
					// Verifica validade da mensagem
					String message = new String(raw, "UTF8");
					char type = header.type;
					int startOfSignature = header.startOfSignature;
					// Recupera a chave pública do remetente da lista
					// PublicKey senderPublicKey = this.nodesPubKeys.get(senderID);
					// this.sig.initVerify(senderPublicKey);

					// System.out.printf("[%s]: %s\n", senderID.toString(), message.substring(36));
				}

			}
		} catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
			System.out.println("Public Key: " + e.getMessage());
		} catch (IOException e) {
			System.out.println("IO: " + e.getMessage());
		}
	}

	// Getters e Setters
	public UUID getUUID() {
		return this.uuid;
	}

	public void setUUID(UUID uuid) {
		this.uuid = uuid;
		System.out.println("Your ID is: " + this.uuid);
	}

	public InetAddress getGroup() {
		return group;
	}

	public void setGroup(InetAddress group) {
		this.group = group;
	}

}
