# itudb2155
BLG317E Database Project

Projede iki user type var biri admin diğeri normal user. Admin proje üzerinde bir çok crud operasyonu yapabiliyor yani admin hesabına ihtiyaç mevuct. Bir kullanıcının admin olabilmesi için database manager tarafından admin yapılması gerekmekte bunu böyle yapmamın sebebi güvenlik ve validasyonu sağlamaktı. 
Bir kullanıcıyı admin yapmak isterseniz çok kısa DB'de UPDATE users is_admin = 'true WHEN id = 'x' //or// username = 'x' şeklinde yapabilirsiniz. (user tablosu main tablolarımdan biri değil)
