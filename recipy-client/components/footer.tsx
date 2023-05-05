import Link from 'next/link'
export default function Footer() {
    return (
        <footer className="fixed bottom-2 p-rounded-lg shadow md:flex md:items-center md:justify-between md:p-6 dark:bg-transperent ">
            <span className="text-sm text-gray-500 sm:text-center dark:text-gray-400">© {new Date().getFullYear()} <Link href="/about" className="hover:underline">ReciPy</Link>
            </span>
            <ul className="flex flex-wrap justify-end items-right mt-3 text-sm text-gray-500 dark:text-gray-400 sm:mt-0">
                <li>
                    <p>{"    "}</p>
                </li>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  
                <li>
                    <a href="#" className="mr-4 hover:underline md:mr-6 ">  About</a>
                </li>

            </ul>
        </footer>
    )


} 