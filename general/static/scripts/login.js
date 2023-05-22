$("#loginForm").submit(function(e) {
    e.preventDefault();
    var nama = $("#nama").val();
    var email = $("#email").val();
    console.log(nama)

    $.ajax({
        url: '/login/auth',
        data: {
            'nama': nama,
            'email': email
        },
        dataType: 'json',
        success: function (data) {
            if(data.status === 'success') {
                window.location.href = '/';
            } else {
                alert("Email atau password yang Anda masukan salah!");
            }
        }
    });

})