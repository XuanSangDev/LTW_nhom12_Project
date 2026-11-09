
const API_URL = "/api";

// Gửi yêu cầu hỗ trợ
async function guiYeuCau(data) {
    try {
        const response = await fetch(`${API_URL}/requests`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.message);
            return;
        }

        alert(
            "Gửi yêu cầu thành công!\nMã yêu cầu: "
            + result.code
        );

        window.location.href = "/myhotro";

    } catch (error) {
        alert("Không thể kết nối đến máy chủ!");
        console.error(error);
    }
}


// Lấy danh sách yêu cầu
async function layDanhSachYeuCau() {
    try {
        const response = await fetch(
            `${API_URL}/requests`
        );

        const result = await response.json();

        return result.requests;

    } catch (error) {
        console.error(error);
        return [];
    }
}


// Lấy chi tiết yêu cầu
async function layChiTietYeuCau(maYeuCau) {
    try {
        const response = await fetch(
            `${API_URL}/requests/${encodeURIComponent(maYeuCau)}`
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message);
        }

        return result.request;

    } catch (error) {
        console.error(error);
        return null;
    }
}


// Gửi phản hồi
async function guiPhanHoi(maYeuCau, noiDung) {
    try {
        const response = await fetch(
            `${API_URL}/requests/${encodeURIComponent(maYeuCau)}/replies`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: noiDung
                })
            }
        );

        const result = await response.json();

        if (!response.ok) {
            alert(result.message);
            return false;
        }

        alert("Gửi phản hồi thành công!");
        return true;

    } catch (error) {
        alert("Lỗi kết nối máy chủ!");
        return false;
    }
}


// Tìm kiếm FAQ
async function timKiemFAQ(tuKhoa = "") {
    try {
        const response = await fetch(
            `${API_URL}/faqs?q=${encodeURIComponent(tuKhoa)}`
        );

        const result = await response.json();

        return result.faqs;

    } catch (error) {
        console.error(error);
        return [];
    }
}


// Lấy thống kê
async function layThongKe() {
    try {
        const response = await fetch(
            `${API_URL}/statistics`
        );

        return await response.json();

    } catch (error) {
        console.error(error);
        return null;
    }
}


// ======================================
// THU GỌN / MỞ RỘNG MENU HỖ TRỢ NGƯỜI HỌC
// ======================================

function toggleSupportMenu() {
    const submenu = document.getElementById("supportSubmenu");
    const arrow = document.getElementById("supportArrow");
    const toggle = document.getElementById("supportToggle");

    if (!submenu || !arrow || !toggle) return;

    const isOpen = toggle.getAttribute("aria-expanded") === "true";

    if (isOpen) {
        submenu.classList.add("hidden");
        arrow.classList.add("rotate-180");
        toggle.setAttribute("aria-expanded", "false");
    } else {
        submenu.classList.remove("hidden");
        arrow.classList.remove("rotate-180");
        toggle.setAttribute("aria-expanded", "true");
    }
}



const uploadArea = document.getElementById("upload-area");
const fileInput = document.getElementById("attachment");
const chooseButton = document.getElementById("choose-file");
const filePreview = document.getElementById("file-preview");

const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");

let selectedFile = null;

const allowedExtensions = ["png", "jpg", "jpeg", "pdf"];
const maxSize = 10 * 1024 * 1024;

// Kiểm tra và hiển thị tệp
function handleFile(file) {
    if (!file) return;

    const extension = file.name.split(".").pop().toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        alert("Chỉ chấp nhận tệp PNG, JPG, JPEG hoặc PDF!");
        return;
    }

    if (file.size > maxSize) {
        alert("Dung lượng tệp không được vượt quá 10MB!");
        return;
    }

    selectedFile = file;

    // Hiển thị thông tin tệp
    fileName.textContent = file.name;
    fileSize.textContent =
        (file.size / 1024 / 1024).toFixed(2) + " MB";

    filePreview.classList.remove("hidden");
    filePreview.classList.add("flex");

    // Đồng bộ tệp vào input để Flask nhận được
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;
}

// ==============================
// XỬ LÝ TẢI TỆP ĐÍNH KÈM
// ==============================

if (
    uploadArea &&
    fileInput &&
    chooseButton &&
    filePreview &&
    fileName &&
    fileSize
) {
    // Mở cửa sổ chọn tệp
    chooseButton.addEventListener("click", function () {
        fileInput.click();
    });

    // Nhấn vào vùng tải tệp
    uploadArea.addEventListener("click", function (event) {
        if (event.target.closest("button")) return;
        fileInput.click();
    });

    // Khi chọn tệp
    fileInput.addEventListener("change", function () {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });

    // Kéo tệp vào vùng tải
    uploadArea.addEventListener("dragover", function (event) {
        event.preventDefault();
        uploadArea.classList.add("border-blue-500", "bg-blue-50");
    });

    uploadArea.addEventListener("dragleave", function () {
        uploadArea.classList.remove("border-blue-500", "bg-blue-50");
    });

    uploadArea.addEventListener("drop", function (event) {
        event.preventDefault();
        uploadArea.classList.remove("border-blue-500", "bg-blue-50");

        const file = event.dataTransfer.files[0];
        if (file) handleFile(file);
    });

    // Xem trước tệp vừa chọn
    const previewButton = document.getElementById("preview-file");

    if (previewButton) {
        previewButton.addEventListener("click", function () {
            if (!selectedFile) return;

            const url = URL.createObjectURL(selectedFile);
            window.open(url, "_blank");
        });
    }

    // Xóa tệp
    const removeButton = document.getElementById("remove-file");

    if (removeButton) {
        removeButton.addEventListener("click", function () {
            selectedFile = null;
            fileInput.value = "";

            filePreview.classList.add("hidden");
            filePreview.classList.remove("flex");

            fileName.textContent = "";
            fileSize.textContent = "";
        });
    }
}

function copyStudentInfo() {
    const studentInfo = `Nguyễn Văn An
MSV: 11223344
Email: an.nv@neu.edu.vn
Khoa CNTT`;

    navigator.clipboard.writeText(studentInfo)

        .catch(() => {
            alert("Không thể sao chép thông tin!");
        });
}


document.addEventListener("DOMContentLoaded", function () {

    const replyChooseButton = document.getElementById("reply-choose-file");
    const replyFileInput = document.getElementById("reply-attachment");
    const replyFilePreview = document.getElementById("reply-file-preview");

    if (!replyChooseButton || !replyFileInput || !replyFilePreview) {
        return;
    }

    // Danh sách file đã chọn
    let replySelectedFiles = [];

    // Mở cửa sổ chọn file
    replyChooseButton.addEventListener("click", function () {
        replyFileInput.click();
    });

    // Định dạng dung lượng
    function formatReplyFileSize(size) {
        if (size < 1024 * 1024) {
            return (size / 1024).toFixed(1) + " KB";
        }

        return (size / (1024 * 1024)).toFixed(2) + " MB";
    }

    // Chọn biểu tượng theo loại file
    function getReplyFileIcon(file) {
        const extension = file.name.split(".").pop().toLowerCase();

        if (file.type.startsWith("image/")) {
            return "fa-file-image text-blue-500";
        }

        if (extension === "pdf") {
            return "fa-file-pdf text-red-500";
        }

        if (["doc", "docx"].includes(extension)) {
            return "fa-file-word text-blue-600";
        }

        if (["xls", "xlsx"].includes(extension)) {
            return "fa-file-excel text-green-600";
        }

        if (extension === "zip") {
            return "fa-file-zipper text-yellow-600";
        }

        return "fa-file text-slate-500";
    }

    // Cập nhật danh sách file vào input để có thể gửi lên Flask
    function updateReplyInputFiles() {
        const dataTransfer = new DataTransfer();

        replySelectedFiles.forEach(function (file) {
            dataTransfer.items.add(file);
        });

        replyFileInput.files = dataTransfer.files;
    }

    // Hiển thị danh sách file
    function renderReplyFiles() {
        replyFilePreview.innerHTML = "";

        replySelectedFiles.forEach(function (file, index) {

            const item = document.createElement("div");

            item.className =
                "relative border border-slate-200 rounded-lg p-3 bg-slate-50";

            // Phần thông tin file
            const info = document.createElement("div");
            info.className = "flex items-center gap-3";

            const icon = document.createElement("i");
            icon.className =
                "fa-solid " + getReplyFileIcon(file) + " text-2xl";

            const details = document.createElement("div");
            details.className = "min-w-0 flex-1";

            const name = document.createElement("p");
            name.className =
                "text-xs font-medium text-slate-700 truncate";
            name.textContent = file.name;

            const size = document.createElement("p");
            size.className = "text-[11px] text-slate-400 mt-1";
            size.textContent = formatReplyFileSize(file.size);

            details.appendChild(name);
            details.appendChild(size);

            // Nút xóa file
            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.className =
                "text-slate-400 hover:text-red-500 p-1";
            removeButton.innerHTML =
                '<i class="fa-solid fa-xmark"></i>';

            removeButton.title = "Xóa tệp";

            removeButton.addEventListener("click", function () {
                replySelectedFiles.splice(index, 1);
                updateReplyInputFiles();
                renderReplyFiles();
            });

            info.appendChild(icon);
            info.appendChild(details);
            info.appendChild(removeButton);

            item.appendChild(info);

            // Xem trước ảnh
            if (file.type.startsWith("image/")) {

                const image = document.createElement("img");

                image.src = URL.createObjectURL(file);
                image.alt = file.name;

                image.className =
                    "mt-3 w-full h-36 object-contain rounded-lg bg-white border border-slate-200";

                item.appendChild(image);
            }

            replyFilePreview.appendChild(item);
        });
    }

    // Khi người dùng chọn file
    replyFileInput.addEventListener("change", function () {

        const newFiles = Array.from(replyFileInput.files);

        newFiles.forEach(function (file) {

            // Không thêm trùng file
            const alreadyExists = replySelectedFiles.some(function (existing) {
                return existing.name === file.name &&
                       existing.size === file.size &&
                       existing.lastModified === file.lastModified;
            });

            if (!alreadyExists) {
                replySelectedFiles.push(file);
            }
        });

        updateReplyInputFiles();
        renderReplyFiles();
    });

});

// ==============================
// PHÂN TRANG YÊU CẦU HỖ TRỢ
// ==============================

function showPage(page) {
    const page1 = document.getElementById("page-1");
    const page2 = document.getElementById("page-2");

    const btn1 = document.getElementById("btn-page-1");
    const btn2 = document.getElementById("btn-page-2");

    if (!page1 || !page2 || !btn1 || !btn2) return;

    page1.style.display = page === 1 ? "table-row-group" : "none";
    page2.style.display = page === 2 ? "table-row-group" : "none";

    btn1.classList.toggle("bg-slate-900", page === 1);
    btn1.classList.toggle("text-white", page === 1);

    btn2.classList.toggle("bg-slate-900", page === 2);
    btn2.classList.toggle("text-white", page === 2);
}

// ==============================
// XEM TRƯỚC ẢNH ĐÍNH KÈM
// ==============================

function previewAttachment(filename) {
    const modal = document.getElementById("preview-modal");
    const image = document.getElementById("preview-image");

    if (!modal || !image) return;

    image.src = "/static/uploads/" + encodeURIComponent(filename);

    modal.classList.remove("hidden");
    modal.classList.add("flex");
}

function closePreview() {
    const modal = document.getElementById("preview-modal");
    const image = document.getElementById("preview-image");

    if (!modal || !image) return;

    modal.classList.add("hidden");
    modal.classList.remove("flex");
    image.src = "";
}

// ==============================
// ĐÁNH GIÁ 5 SAO
// ==============================

function initRating() {
    const ratingContainer = document.getElementById("rating-stars");
    const message = document.getElementById("rating-message");

    if (!ratingContainer || !message) return;

    const stars = ratingContainer.querySelectorAll("[data-rating]");

    stars.forEach(star => {
        star.addEventListener("click", function () {
            const selectedRating = Number(this.dataset.rating);

            stars.forEach(item => {
                const value = Number(item.dataset.rating);
                const isSelected = value <= selectedRating;

                item.classList.toggle("fa-solid", isSelected);
                item.classList.toggle("fa-regular", !isSelected);
                item.classList.toggle("text-amber-400", isSelected);
                item.classList.toggle("text-slate-300", !isSelected);
            });

            message.textContent =
                `Bạn đã đánh giá ${selectedRating}/5 sao`;
        });
    });
}

// Đảm bảo HTML đã được tải trước khi chạy
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRating);
} else {
    initRating();
}


/* ==========================================
   UPLOAD TỆP ĐÍNH KÈM TRONG TRANG CHI TIẾT
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    const replyUploadArea = document.getElementById("reply-upload-area");
    const replyFileInput = document.getElementById("reply-attachment");
    const replyChooseButton = document.getElementById("reply-choose-file");
    const replyFilePreview = document.getElementById("reply-file-preview");

    // Chỉ chạy khi các phần tử tồn tại
    if (!replyUploadArea || !replyFileInput ||
        !replyChooseButton || !replyFilePreview) {
        return;
    }

    const MAX_SIZE = 10 * 1024 * 1024;

    const allowedExtensions = [
        "png", "jpg", "jpeg", "pdf",
        "doc", "docx", "xls", "xlsx",
        "txt", "zip"
    ];

    let replySelectedFiles = [];

    // Kiểm tra tệp
    function validateReplyFile(file) {
        const extension = file.name.split(".").pop().toLowerCase();

        if (!allowedExtensions.includes(extension)) {
            alert(`Tệp ${file.name} không đúng định dạng cho phép!`);
            return false;
        }

        if (file.size > MAX_SIZE) {
            alert(`Tệp ${file.name} vượt quá dung lượng 10MB!`);
            return false;
        }

        return true;
    }

    // Định dạng dung lượng
    function formatReplyFileSize(size) {
        if (size < 1024 * 1024) {
            return (size / 1024).toFixed(1) + " KB";
        }

        return (size / (1024 * 1024)).toFixed(2) + " MB";
    }

    // Chọn biểu tượng theo loại tệp
    function getReplyFileIcon(file) {
        const extension = file.name.split(".").pop().toLowerCase();

        if (["png", "jpg", "jpeg"].includes(extension)) {
            return "fa-file-image text-blue-500";
        }

        if (extension === "pdf") {
            return "fa-file-pdf text-red-500";
        }

        if (["doc", "docx"].includes(extension)) {
            return "fa-file-word text-blue-600";
        }

        if (["xls", "xlsx"].includes(extension)) {
            return "fa-file-excel text-green-600";
        }

        if (extension === "zip") {
            return "fa-file-zipper text-yellow-600";
        }

        return "fa-file-lines text-slate-500";
    }

    // Đồng bộ danh sách tệp vào input
    function updateReplyInputFiles() {
        const dataTransfer = new DataTransfer();

        replySelectedFiles.forEach(file => {
            dataTransfer.items.add(file);
        });

        replyFileInput.files = dataTransfer.files;
    }

    // Hiển thị danh sách tệp
    function renderReplyFiles() {
        replyFilePreview.innerHTML = "";

        if (replySelectedFiles.length === 0) {
            replyFilePreview.classList.add("hidden");
            return;
        }

        replyFilePreview.classList.remove("hidden");

        replySelectedFiles.forEach((file, index) => {

            const item = document.createElement("div");

            item.className =
                "flex items-center justify-between gap-3 p-3 bg-white border border-slate-200 rounded-lg";

            // Thông tin tệp
            const info = document.createElement("div");
            info.className = "flex items-center gap-3 min-w-0";

            const icon = document.createElement("i");
            icon.className =
                "fa-solid " + getReplyFileIcon(file) + " text-xl";

            const details = document.createElement("div");
            details.className = "min-w-0";

            const name = document.createElement("p");
            name.className =
                "text-xs font-medium text-slate-700 truncate";
            name.textContent = file.name;

            const size = document.createElement("p");
            size.className = "text-[11px] text-slate-400 mt-1";
            size.textContent = formatReplyFileSize(file.size);

            details.appendChild(name);
            details.appendChild(size);

            info.appendChild(icon);
            info.appendChild(details);

            // Nhóm nút thao tác
            const actions = document.createElement("div");
            actions.className = "flex items-center gap-3 shrink-0";

            // Nút xem trước
            const previewButton = document.createElement("button");
            previewButton.type = "button";
            previewButton.className =
                "text-blue-500 hover:text-blue-700";
            previewButton.innerHTML =
                '<i class="fa-solid fa-eye"></i>';
            previewButton.title = "Xem trước";

            previewButton.addEventListener("click", function () {
                const extension = file.name.split(".").pop().toLowerCase();

                if (!["png", "jpg", "jpeg", "pdf"].includes(extension)) {
                    alert("Tệp này chưa hỗ trợ xem trước trực tiếp.");
                    return;
                }

                const fileURL = URL.createObjectURL(file);
                const newWindow = window.open(fileURL, "_blank");

                if (newWindow) {
                    setTimeout(() => {
                        URL.revokeObjectURL(fileURL);
                    }, 60000);
                } else {
                    URL.revokeObjectURL(fileURL);
                    alert("Trình duyệt đang chặn cửa sổ xem trước.");
                }
            });

            // Nút xóa
            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className =
                "text-red-500 hover:text-red-700";
            deleteButton.innerHTML =
                '<i class="fa-solid fa-trash"></i>';
            deleteButton.title = "Xóa tệp";

            deleteButton.addEventListener("click", function () {
                replySelectedFiles.splice(index, 1);

                updateReplyInputFiles();
                renderReplyFiles();
            });

            actions.appendChild(previewButton);
            actions.appendChild(deleteButton);

            item.appendChild(info);
            item.appendChild(actions);

            replyFilePreview.appendChild(item);
        });
    }

    // Thêm tệp vào danh sách
    function addReplyFiles(files) {

        Array.from(files).forEach(file => {

            if (!validateReplyFile(file)) return;

            // Không thêm tệp trùng
            const duplicated = replySelectedFiles.some(existing =>
                existing.name === file.name &&
                existing.size === file.size &&
                existing.lastModified === file.lastModified
            );

            if (!duplicated) {
                replySelectedFiles.push(file);
            }
        });

        updateReplyInputFiles();
        renderReplyFiles();
    }

    // Bấm nút chọn tệp
    replyChooseButton.addEventListener("click", function (event) {
        event.stopPropagation();
        replyFileInput.click();
    });

    // Bấm vào vùng tải tệp
    replyUploadArea.addEventListener("click", function (event) {
        if (event.target.closest("button")) return;

        replyFileInput.click();
    });

    // Chọn tệp từ máy tính
    replyFileInput.addEventListener("change", function () {
        addReplyFiles(this.files);

        // Cho phép chọn lại tệp đã chọn trước đó
        this.value = "";
        updateReplyInputFiles();
    });

    // Kéo tệp vào vùng tải
    replyUploadArea.addEventListener("dragover", function (event) {
        event.preventDefault();

        replyUploadArea.classList.add(
            "border-blue-500",
            "bg-blue-50"
        );
    });

    // Kéo tệp ra khỏi vùng tải
    replyUploadArea.addEventListener("dragleave", function () {
        replyUploadArea.classList.remove(
            "border-blue-500",
            "bg-blue-50"
        );
    });

    // Thả tệp vào vùng tải
    replyUploadArea.addEventListener("drop", function (event) {
        event.preventDefault();

        replyUploadArea.classList.remove(
            "border-blue-500",
            "bg-blue-50"
        );

        addReplyFiles(event.dataTransfer.files);
    });

});


// ======================================
// GỬI PHẢN HỒI VÀ HIỂN THỊ TIN NHẮN MỚI
// ======================================

document.addEventListener("DOMContentLoaded", function () {

    const messageList = document.getElementById("message-list");
    const replyContent = document.getElementById("reply-content");
    const sendButton = document.getElementById("send-reply");

    if (!messageList || !replyContent || !sendButton) {
        return;
    }

    sendButton.addEventListener("click", function () {

        const content = replyContent.value.trim();

        if (content === "") {
            alert("Vui lòng nhập nội dung phản hồi!");
            replyContent.focus();
            return;
        }

        const now = new Date();

        const time = now.toLocaleDateString("vi-VN") + " • " +
            now.toLocaleTimeString("vi-VN", {
                hour: "2-digit",
                minute: "2-digit"
            });

        // Tạo tin nhắn mới
        const message = document.createElement("div");

        message.className = "flex items-start gap-3";

        message.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-[#1e293b] text-white text-xs font-semibold flex items-center justify-center shrink-0 mt-0.5">
                VA
            </div>

            <div class="flex-1 bg-white border border-blue-200 rounded-xl p-4 shadow-sm space-y-2">

                <div class="flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2">
                        <span class="font-bold text-slate-900 text-sm">
                            Nguyễn Văn An
                        </span>

                        <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-600 border border-blue-100">
                            Sinh viên
                        </span>
                    </div>

                    <span class="text-slate-400">${time}</span>
                </div>

                <p class="text-xs md:text-[13px] text-slate-700 leading-relaxed whitespace-pre-wrap"></p>

            </div>
        `;

        // Hiển thị nội dung phản hồi
        message.querySelector("p").textContent = content;

        // Thêm tin nhắn vào danh sách
        messageList.appendChild(message);

        // Xóa nội dung đã nhập
        replyContent.value = "";

        // Cuộn đến tin nhắn mới
        message.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    });

});


// ======================================
// FAQ ACCORDION - MỞ / ĐÓNG CÂU HỎI
// ======================================

document.addEventListener("DOMContentLoaded", function () {

    const faqItems = document.querySelectorAll(".faq-item");

    faqItems.forEach(item => {

        const toggle = item.querySelector(".faq-toggle");
        const content = item.querySelector(".faq-content");
        const icon = item.querySelector(".faq-icon");
        const number = item.querySelector(".faq-number");

        if (!toggle || !content || !icon || !number) return;

        toggle.addEventListener("click", function () {

            const isCurrentlyOpen =
                toggle.getAttribute("aria-expanded") === "true";

            // Đóng tất cả câu hỏi
            faqItems.forEach(otherItem => {

                const otherToggle = otherItem.querySelector(".faq-toggle");
                const otherContent = otherItem.querySelector(".faq-content");
                const otherIcon = otherItem.querySelector(".faq-icon");
                const otherNumber = otherItem.querySelector(".faq-number");

                if (!otherToggle || !otherContent ||
                    !otherIcon || !otherNumber) return;

                otherToggle.setAttribute("aria-expanded", "false");

                otherContent.classList.add("hidden");

                otherIcon.classList.remove("fa-chevron-up");
                otherIcon.classList.add("fa-chevron-down");

                otherNumber.classList.remove(
                    "bg-[#0F1A30]", "text-white"
                );

                otherNumber.classList.add(
                    "bg-slate-100", "text-slate-600"
                );
            });

            // Nếu câu hỏi vừa bấm đang đóng thì mở nó
            if (!isCurrentlyOpen) {

                toggle.setAttribute("aria-expanded", "true");

                content.classList.remove("hidden");

                icon.classList.remove("fa-chevron-down");
                icon.classList.add("fa-chevron-up");

                number.classList.remove(
                    "bg-slate-100", "text-slate-600"
                );

                number.classList.add(
                    "bg-[#0F1A30]", "text-white"
                );
            }

        });

    });

});

