export default function Button({ children, onClick, type = "button", variant = "primary" }) {
    return (
        <button
            className={`btn btn-${variant}`}
            onClick={onClick}
            type={type}
        >
            {children}
        </button>
    );
}
