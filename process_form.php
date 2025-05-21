<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nome = htmlspecialchars($_POST['nome']);
    $email = htmlspecialchars($_POST['email']);
    $assunto = htmlspecialchars($_POST['assunto']);
    $msg = htmlspecialchars($_POST['msg']);

    $to = "suporte@zveiter.adv.br";
    $subject = "Formulário de Contato: $assunto";
    $message = "Nome: $nome\nE-mail: $email\n\nMensagem:\n$msg";
    $headers = "From: $email";

    if (mail($to, $subject, $message, $headers)) {
        echo "Mensagem enviada com sucesso!";
    } else {
        echo "Falha no envio da mensagem.";
    }
}
?>
